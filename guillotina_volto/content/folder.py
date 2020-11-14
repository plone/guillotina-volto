# -*- encoding: utf-8 -*-
from guillotina import configure
from guillotina.content import Folder
from guillotina_volto.interfaces import ICMSFolder


@configure.contenttype(
    type_name="CMSFolder",
    schema=ICMSFolder,
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina_volto.interfaces.base.ICMSBehavior",
        "guillotina_volto.interfaces.blocks.IBlocks",
    ],
)
class CMSFolder(Folder):
    pass
