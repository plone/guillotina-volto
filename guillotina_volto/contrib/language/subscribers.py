from guillotina import configure
from guillotina.content import create_content_in_container
from guillotina.event import notify
from guillotina.events import ObjectAddedEvent
from guillotina.events import ObjectModifiedEvent
from guillotina.interfaces import IAddons
from guillotina.interfaces import IObjectAddedEvent
from guillotina.interfaces import IObjectRemovedEvent
from guillotina.interfaces import IResource
from guillotina.utils import get_behavior
from guillotina.utils import get_content_path
from guillotina.utils import get_current_container
from guillotina.utils import get_object_by_uid
from guillotina.utils import get_object_url
from guillotina.utils import get_registry
from guillotina.utils import navigate_to
from guillotina.utils import resolve_dotted_name

from guillotina_volto.contrib.language.behaviors import ILanguageBehavior
from guillotina_volto.contrib.language.interfaces import ILanguageFolder
from guillotina_volto.interfaces.events import IRegistryChangedEvent
from guillotina_volto.utils import Search


@configure.subscriber(for_=(IRegistryChangedEvent))
async def registry_modified(event):
    if event.id_ == "language":
        registry = await get_registry()
        config = registry.for_interface(IAddons)
        # if "language" not in config["enabled"]:
        #     raise HTTPBadRequest(content={"message": "Language addon not installed"})
        site = event.site
        schemaObj = resolve_dotted_name("guillotina_volto.contrib.language.interfaces.ILanguageSettings")
        config = registry.for_interface(schemaObj)
        available_languages = config.__getitem__("available_languages")
        site = event.site
        language_folder_path = get_object_url(site)
        for language in available_languages:
            result = await site.async_contains(language)
            lan_folder = None
            if result is False:
                lan_folder = await create_content_in_container(site, "LanguageFolder", language, check_security=False)
                await notify(ObjectAddedEvent(lan_folder, site))
            else:
                lan_folder = await site.async_get(language)
            bhr = await get_behavior(lan_folder, ILanguageBehavior)
            if bhr.translations == {}:
                bhr.translations = {}
            bhr.language = language
            for other_language in available_languages:
                if other_language != language:
                    payload_translation = {
                        "@id": f"{language_folder_path}/{other_language}",
                        "language": other_language,
                    }
                    bhr.translations[other_language] = payload_translation
            bhr.register()


@configure.subscriber(for_=(IResource, IObjectAddedEvent))
async def resource_added(context, event):
    # Get the translation_of
    payload = event.payload
    if payload is not None and "translation_of" in payload:
        bhr = await get_behavior(context, ILanguageBehavior)
        await bhr.link_translation(payload["translation_of"])


@configure.subscriber(for_=(IResource, IObjectRemovedEvent))
async def resource_deleted(context, event):
    bhr = await get_behavior(context, ILanguageBehavior)
    container = get_current_container()
    current_path = get_content_path(context)
    if bhr:
        paths_already_deleted = []
        for path, translation in bhr.translations.items():
            try:
                obj = await navigate_to(container, path)
            except KeyError:
                # Object is being deleted, we do not care if its
                # translations are not well synced
                continue
            bhr_obj_translated = await get_behavior(obj, ILanguageBehavior)
            bhr_obj_translated.translations.pop(current_path, None)
            bhr_obj_translated.register()
            obj.register()
        for path_to_delete in paths_already_deleted:
            bhr.translations.pop(path_to_delete, None)


@configure.subscriber(for_=(ILanguageFolder, IObjectRemovedEvent))
async def language_folder_deleted(context, event):
    search_instance = Search()
    starts_with_language = f"/{context.id}"
    results = await search_instance.search_raw(
        unrestricted=False, query={"paths_indexed__starts": starts_with_language}
    )
    for result in results["items"]:
        obj = await get_object_by_uid(result["uuid"])
        bhr = await get_behavior(obj, ILanguageBehavior)
        keys_to_delete = set()
        for translation in bhr.translations.keys():
            if translation.startswith(starts_with_language):
                keys_to_delete.add(translation)
        for key_to_delete in keys_to_delete:
            bhr.translations.pop(key_to_delete, None)
        bhr.register()
        obj.register()
        await notify(ObjectModifiedEvent(bhr, payload={"translations": bhr.translations}))
