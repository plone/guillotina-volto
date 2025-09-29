from guillotina import configure
from guillotina.interfaces import IResource
from guillotina.interfaces import IObjectAddedEvent
from guillotina.utils import get_behavior
from guillotina_volto.interfaces import ICMSBehavior
from guillotina.component import get_multi_adapter
from guillotina.interfaces import IResourceSerializeToJson
from guillotina.utils import get_current_request
from guillotina.utils import get_authenticated_user_id
from datetime import datetime
from guillotina.event import notify
from guillotina.events import ObjectModifiedEvent


@configure.subscriber(for_=(IResource, IObjectAddedEvent))
async def object_created(context, event):
    request = get_current_request()
    bhr = await get_behavior(context, ICMSBehavior)
    serializer = get_multi_adapter((context, request), IResourceSerializeToJson)
    obj_serialized = None
    if serializer:
        obj_serialized = await serializer()
    await bhr.load(create=True)
    payload = {
        "actor": get_authenticated_user_id(),
        "comments": "Initial version",
        "time": datetime.utcnow().timestamp(),
        "type": context.type_name,
        "title": "Object created",
        "data": obj_serialized,
    }
    bhr.history = {"0": payload}
    bhr.register()
