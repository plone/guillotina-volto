from guillotina import configure
from guillotina.content import Folder
from guillotina_volto.contrib.language.interfaces import ILanguageFolder


@configure.contenttype(
    type_name="LanguageFolder",
    schema=ILanguageFolder,
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina.contrib.workflows.interfaces.IWorkflowBehavior",
        "guillotina_volto.interfaces.base.ICMSBehavior",
        "guillotina_volto.interfaces.blocks.IBlocks",
    ],
)
class LanguageFolder(Folder):
    pass
