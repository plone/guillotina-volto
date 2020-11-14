from guillotina import configure
from guillotina.behaviors.instance import ContextBehavior
from guillotina_volto.interfaces import IBlocks
from guillotina.directives import index


@configure.behavior(
    title="Blocks behavior",
    provides=IBlocks,
    for_="guillotina.interfaces.IResource",
)
class Blocks(ContextBehavior):
    pass


