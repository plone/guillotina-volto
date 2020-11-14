# -*- encoding: utf-8 -*-
from guillotina_volto.interfaces.content import ISite
from guillotina import configure
from guillotina.content import Container


@configure.contenttype(
    type_name="Site",
    schema=ISite,
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina_volto.interfaces.base.ICMSBehavior",
        "guillotina_volto.interfaces.blocks.IBlocks",
    ],
)
class Site(Container):
    pass
