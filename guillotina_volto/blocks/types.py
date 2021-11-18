from zope.interface import implementer

from guillotina_volto.interfaces import IBlockType


@implementer(IBlockType)
class BlockType(object):
    pass
