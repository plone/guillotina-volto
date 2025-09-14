from guillotina import configure
from guillotina.behaviors.dublincore import IDublinCore
from guillotina.component import get_utility
from guillotina.content import load_cached_schema
from guillotina.interfaces import IApplicationInitializedEvent
from guillotina.interfaces import IResourceFactory

from guillotina_volto.interfaces.base import ICMSBehavior
from guillotina_volto.interfaces.blocks import IBlocks


@configure.subscriber(for_=IApplicationInitializedEvent)
async def app_initialized(event):
    factory = get_utility(IResourceFactory, "Container")
    # factory = get_cached_factory("Container")
    factory.behaviors = (IDublinCore, ICMSBehavior, IBlocks)
    load_cached_schema()
