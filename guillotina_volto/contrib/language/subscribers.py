from guillotina import configure
from guillotina_volto.interfaces.events import IRegistryChangedEvent
from guillotina.utils import get_registry
from guillotina.interfaces import IAddons
from guillotina.response import HTTPBadRequest
from guillotina.utils import resolve_dotted_name
from guillotina.content import create_content_in_container
from guillotina.event import notify
from guillotina.events import ObjectAddedEvent
from guillotina.interfaces import IResource
from guillotina.interfaces import IObjectAddedEvent
from guillotina.utils import get_behavior
from guillotina.utils import get_current_container
from guillotina.utils import get_object_url
from guillotina_volto.contrib.language.behaviors import ILanguageBehavior
from guillotina.utils import navigate_to


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
        for language in available_languages:
            result = await site.async_contains(language)
            if result is False:
                lan_folder = await create_content_in_container(site, "LanguageFolder", language, check_security=False)
                await notify(ObjectAddedEvent(lan_folder, site))


@configure.subscriber(for_=(IResource, IObjectAddedEvent))
async def resource_added(context, event):
    # Get the translation_of
    payload = event.payload
    if payload is not None and "translation_of" in payload:
        current_language = payload["language"]
        translation_of = payload["translation_of"]
        language = translation_of.strip("/").split("/")[0]
        container = get_current_container()
        full_url_container = get_object_url(container)
        payload = {
            "@id": f"{full_url_container}{translation_of}",
            "language": language,
            "path": translation_of
        }
        bhr = await get_behavior(context, ILanguageBehavior)
        current_path = f"/{current_language}/{context.id}"
        # Update all the other transalations. Go over every related
        # one and update them all
        if bhr.translations == []:
            # I need to set this first before doing an append. WHY?
            bhr.translations = []
        bhr.translations.append(payload)
        payload_current_object = {
            "@id": f"{full_url_container}{current_path}",
            "language": current_language,
            "path": current_path
        }
        obj_translated_of = await navigate_to(container, translation_of)
        bhr_obj_translated_from = await get_behavior(obj_translated_of, ILanguageBehavior)
        if bhr_obj_translated_from.translations == []:
            bhr_obj_translated_from.translations = []
        for translation in bhr_obj_translated_from.translations:
            path = translation["path"]
            language = translation["language"]
            try:
                obj_translated_of = await navigate_to(container, path)
            except KeyError:
                continue
            payload = {
                "@id": f"{full_url_container}/{path}",
                "language": language,
                "path": path
            }
            bhr.translations.append(payload)
            bhr_obj_translated = await get_behavior(obj_translated_of, ILanguageBehavior)
            await bhr_obj_translated.load()
            if bhr_obj_translated.translations == []:
                bhr_obj_translated.translations = []
            bhr_obj_translated.translations.append(payload_current_object)
            bhr_obj_translated.register()
            obj_translated_of.register()
        bhr_obj_translated_from.translations.append(payload_current_object)
        bhr_obj_translated_from.register()
        bhr.register()
        context.register()
