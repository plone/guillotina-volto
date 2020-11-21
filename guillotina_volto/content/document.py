# -*- encoding: utf-8 -*-
from guillotina import configure
from guillotina.content import Folder
from guillotina.directives import index
from guillotina_volto.interfaces import IDocument


@configure.contenttype(
    type_name="Document",
    schema=IDocument,
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina.contrib.workflows.interfaces.IWorkflowBehavior",
        "guillotina_volto.interfaces.base.ICMSBehavior",
        "guillotina_volto.interfaces.blocks.IBlocks",
    ],
    allowed_types=["Image", "File"],  # dynamically calculated
)
class Document(Folder):
    pass
