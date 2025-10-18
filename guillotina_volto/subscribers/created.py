from datetime import datetime

from dateutil.tz import tzutc
from guillotina import configure
from guillotina.component import get_multi_adapter
from guillotina.interfaces import IObjectAddedEvent
from guillotina.interfaces import IResource
from guillotina.interfaces import IResourceSerializeToJson
from guillotina.utils import get_authenticated_user_id
from guillotina.utils import get_behavior
from guillotina.utils import get_current_request

from guillotina_volto.interfaces import ICMSBehavior


_zone = tzutc()  # utz tz is much faster than local tz info


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
        "time": datetime.now(tz=_zone),
        "type": "versioning",
        "title": "Object created",
        "data": obj_serialized,
    }
    bhr.history = {"0": payload}
    bhr.register()
