# -*- coding: utf-8 -*-
from guillotina import configure
from guillotina.addons import Addon


@configure.addon(name="language", title="Multi Language Addon")
class LanguageAddon(Addon):
    @classmethod
    async def install(cls, container, request):
        pass

    @classmethod
    async def uninstall(cls, container, request):
        pass
