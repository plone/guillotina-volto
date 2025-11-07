# -*- encoding: utf-8 -*-
from guillotina import configure
from guillotina.content import Folder

from guillotina_volto.interfaces import IPage


@configure.contenttype(
    type_name="Page",
    schema=IPage,
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina.contrib.workflows.interfaces.IWorkflowBehavior",
        "guillotina_volto.interfaces.base.ICMSBehavior",
        "guillotina_volto.interfaces.blocks.IBlocks",
        "guillotina_volto.interfaces.image.IImagePreviewLinkAttachment"
    ],
)
class Page(Folder):
    pass
