# -*- encoding: utf-8 -*-
from guillotina import configure
from guillotina.content import Container

from guillotina_volto.interfaces.content import ISite


@configure.contenttype(
    type_name="Site",
    schema=ISite,
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina.contrib.workflows.interfaces.IWorkflowBehavior",
        "guillotina_volto.interfaces.base.ICMSBehavior",
        "guillotina_volto.interfaces.blocks.IBlocks",
    ],
)
class Site(Container):
    pass
