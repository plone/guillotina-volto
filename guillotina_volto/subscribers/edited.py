from datetime import datetime

from dateutil.tz import tzutc
from guillotina import configure
from guillotina.component import query_adapter
from guillotina.contrib.workflows.interfaces import IWorkflow
from guillotina.contrib.workflows.interfaces import IWorkflowBehavior
from guillotina.contrib.workflows.interfaces import IWorkflowChangedEvent
from guillotina.events import IObjectPermissionsModifiedEvent
from guillotina.interfaces import IBeforeObjectModifiedEvent
from guillotina.interfaces import IObjectModifiedEvent
from guillotina.interfaces import IResource
from guillotina.utils import get_authenticated_user_id
from guillotina.utils import get_behavior

from guillotina_volto.interfaces import ICMSBehavior
from guillotina_volto.interfaces import IDiffCalculator
from guillotina_volto.interfaces import IVersioning
from guillotina_volto.interfaces import IVersioningMarker


_zone = tzutc()  # utz tz is much faster than local tz info


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
    if IObjectPermissionsModifiedEvent.providedBy(event):
        return
    if "review_state" in event.payload:
        return

    payload = {}
    bhr = await get_behavior(context, ICMSBehavior)
    last_key = list(bhr.history.keys())[-1]
    next_key = str(int(last_key) + 1)
    for key, value in event.payload.items():
        if value is None or value == {}:
            continue
        payload[key] = value
    title = "Object modified"
    if "_v_history" in event.payload:
        version = event.payload["_v_history"]
        title = f"Reverted to revision {version}"
        del payload["_v_history"]
    bhr.history[next_key] = {}
    bhr.history[next_key]["data"] = payload
    bhr.history[next_key]["actor"] = get_authenticated_user_id()
    bhr.history[next_key]["time"] = datetime.now(tz=_zone)
    bhr.history[next_key]["type"] = "versioning"
    bhr.history[next_key]["title"] = title
    bhr.history[next_key]["comments"] = title
    bhr.register()


@configure.subscriber(for_=(IResource, IWorkflowChangedEvent))
async def workflow_changed(context, event):
    workflow = query_adapter(context, IWorkflowBehavior)
    wkf = query_adapter(context, IWorkflow)

    bhr = await get_behavior(context, ICMSBehavior)
    last_key = list(bhr.history.keys())[-1]
    next_key = str(int(last_key) + 1)
    bhr.history[next_key] = {}
    bhr.history[next_key]["actor"] = get_authenticated_user_id()
    bhr.history[next_key]["time"] = datetime.now(tz=_zone)
    bhr.history[next_key]["type"] = "workflow"
    bhr.history[next_key]["title"] = event.action
    bhr.history[next_key]["data"] = {
        "review_state": workflow.review_state,
        "state_title": wkf.states[workflow.review_state]["metadata"]["title"],
    }
    bhr.register()
