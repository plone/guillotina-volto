# -*- coding: utf-8 -*-
from guillotina import configure
from guillotina.addons import Addon
from guillotina.behaviors.dublincore import IDublinCore
from guillotina.interfaces import ILayers
from guillotina.utils import get_registry

from guillotina.content import create_content_in_container
from guillotina.utils import resolve_dotted_name
from guillotina.event import notify
from guillotina.events import ObjectAddedEvent


@configure.addon(name="language", title="Multi Language Addon")
class LanguageAddon(Addon):
    @classmethod
    async def install(cls, container, request):
        pass
        # registry = await get_registry()
        # schema = resolve_dotted_name("guillotina_volto.contrib.language.interfaces.ILanguageSettings")
        # config = registry.for_interface(schema)
        # for language in config.available_languages:
        #     lan_folder = await create_content_in_container(container, "LanguageFolder", language, check_security=False)
        #     await notify(ObjectAddedEvent(lan_folder, container))
        # container.register()

    @classmethod
    async def uninstall(cls, container, request):
        pass
