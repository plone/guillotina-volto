from guillotina import configure
from guillotina.interfaces import IBeforeObjectModifiedEvent
from guillotina.interfaces import IObjectModifiedEvent
from guillotina.interfaces import IResource
from guillotina.utils import get_behavior
from guillotina_volto.interfaces import ICMSBehavior
from guillotina.utils import get_authenticated_user_id
from datetime import datetime

from guillotina_volto.interfaces import IDiffCalculator
from guillotina_volto.interfaces import IVersioning
from guillotina_volto.interfaces import IVersioningMarker


@configure.subscriber(for_=(IVersioningMarker, IBeforeObjectModifiedEvent))
async def before_object_modified(context, event):
    # its enabled to copy the diff
    diff_calculator = IDiffCalculator(event.context, None)
    if diff_calculator is None:
        return
    context._v_temporal_versioning = await diff_calculator(event.payload)


@configure.subscriber(for_=(IResource, IObjectModifiedEvent))
async def object_modified(object, event):
    if IVersioningMarker.providedBy(object):
        version_behavior = IVersioning(object)
        await version_behavior.load(create=True)
        if hasattr(object, "_v_temporal_versioning"):
            version_behavior.diffs.append(object._v_temporal_versioning)
            version_behavior.register()
            del object._v_temporal_versioning


@configure.subscriber(for_=(IResource, IObjectModifiedEvent))
async def modify_history(context, event):
    payload = {}
    bhr = await get_behavior(context, ICMSBehavior)
    last_key = list(bhr.history.keys())[-1]
    next_key = str(int(last_key) + 1)
    for key, value in event.payload.items():
        payload[key] = value
    title = "Object modified"
    if "_v_history" in event.payload:
        version = event.payload["_v_history"]
        title = f"Reverted to revision {version}"
        del payload["_v_history"]
    bhr.history[next_key] = {}
    bhr.history[next_key]["data"] = payload
    bhr.history[next_key]["actor"] = get_authenticated_user_id()
    bhr.history[next_key]["time"] = datetime.utcnow().timestamp()
    bhr.history[next_key]["type"] = context.type_name
    bhr.history[next_key]["title"] = title
    bhr.history[next_key]["comments"] = title
    bhr.register()
