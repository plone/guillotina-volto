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
    if "translation_of" in payload:
        translation_of = payload["translation_of"]
        language = translation_of.strip("/").split("/")[0]
        container = get_current_container()
        full_url_container = get_object_url(container)
        payload = {
            "@id": f"{full_url_container}/{translation_of}",
            "language": language
        }
        bhr = await get_behavior(context, ILanguageBehavior)
        # Update all the other transalations. Go over every related
        # one and update them all
        bhr.translations.append(payload)
