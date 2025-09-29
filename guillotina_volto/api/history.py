import json

from guillotina import configure
from guillotina.component import getMultiAdapter
from guillotina.interfaces import IAbsoluteURL
from guillotina.interfaces import IResource
from guillotina.utils import get_behavior
from guillotina.utils import get_current_container
from guillotina.response import HTTPBadRequest
from guillotina.component import query_multi_adapter
from guillotina.tests.utils import make_mocked_request
from guillotina.interfaces import IResourceDeserializeFromJson
from guillotina.response import ErrorResponse
from guillotina import error_reasons
from guillotina.event import notify
from guillotina.events import BeforeObjectModifiedEvent
from guillotina.events import ObjectModifiedEvent
from guillotina.interfaces import IResourceSerializeToJson
from guillotina.component import get_multi_adapter

from guillotina_volto.interfaces import ICMSBehavior
from guillotina_volto.interfaces import ICMSLayer


@configure.service(
    context=IResource,
    layer=ICMSLayer,
    name="@history",
    method="GET",
    permission="guillotina.SeePermissions",
)
async def history(context, request):
    bhr = await get_behavior(context, ICMSBehavior)
    container = get_current_container()
    result = []
    context_url = getMultiAdapter((context, request), IAbsoluteURL)()
    container_url = getMultiAdapter((container, request), IAbsoluteURL)()
    if bhr.history is None:
        return []
    for ident, hist_data in bhr.history.items():
        actor = hist_data.get("actor", "")
        type_ = hist_data.get("type", "")
        title = hist_data.get("title", "")
        value = {
            "@id": f"{context_url}/@history/{ident}",
            "action": title,
            "comments": hist_data.get("comments", ""),
            "time": hist_data.get("time", ""),
            "transition_title": title,
            "type": type_,
            "actor": {
                "@id": f"{container_url}/@users/{actor}",
                "fullname": actor,
                "id": actor,
                "username": actor,
            },
        }

        data = hist_data.get("data", {})
        if type_ == "versioning":
            value["may_revert"] = False
            value["version"] = ident
        elif type_ == "workflow":
            value["state_title"] = data.get("review_state")
            value["review_state"] = data.get("review_state")
        result.append(value)
    return result


@configure.service(
    context=IResource,
    layer=ICMSLayer,
    name="@history",
    method="PATCH",
    permission="guillotina.ModifyContent",
)
async def history_patch(context, request):
    bhr = await get_behavior(context, ICMSBehavior)
    payload = await request.json()
    if "version" not in payload:
        raise HTTPBadRequest(content={"message": "Needs to pass version"})
    version = str(payload["version"])
    final_values = {}
    # Calculate the final payload to send to the defaultPATCH
    for key, value in reversed(list(bhr.history.items())):
        if key == "0":
            # This is the first version ever created
            for key_final_data, value_final_data in final_values.items():
                if "." in key_final_data:
                    for key_behavior, value_behavior in final_values[
                        key_final_data
                    ].items():
                        # We've came across a behavior
                        final_values[key_final_data][key_behavior] = value["data"][
                            key_final_data
                        ][key_behavior]
                else:
                    try:
                        final_values[key_final_data] = value["data"][key_final_data]
                    except KeyError:
                        # Key not found in the object. This case is
                        # when doing a patch with a key value that
                        # does not exist within the object
                        pass
            break
        for key_data, value_data in value["data"].items():
            final_values[key_data] = value_data
        if key == version:
            break
    # Apply changes
    path = request.path.split("/@history")[0]
    fake_request = make_mocked_request(
        method="PATCH",
        path=path,
        headers=request.headers,
        payload=json.dumps(final_values).encode("utf-8"),
    )
    deserializer = query_multi_adapter(
        (context, fake_request), IResourceDeserializeFromJson
    )
    if deserializer is None:
        raise ErrorResponse(
            "DeserializationError",
            "Cannot deserialize type {}".format(context.type_name),
            status=412,
            reason=error_reasons.DESERIALIZATION_FAILED,
        )
    await notify(BeforeObjectModifiedEvent(context, payload=final_values))
    await deserializer(final_values)
    final_values["_v_history"] = version
    await notify(ObjectModifiedEvent(context, payload=final_values))


@configure.service(
    context=IResource,
    layer=ICMSLayer,
    name="@history/{history}",
    method="GET",
    permission="guillotina.SeePermissions",
)
async def history_get_version(context, request):
    history_version = request.matchdict.get("history")
    bhr = await get_behavior(context, ICMSBehavior)
    serializer = get_multi_adapter((context, request), IResourceSerializeToJson)
    result = await serializer()
    if history_version not in bhr.history:
        raise HTTPBadRequest(content={"message": "History not found"})
    version_changes = bhr.history[history_version]["data"]
    for key_to_change, value_to_change in version_changes.items():
        if key_to_change in result:
            result[key_to_change] = value_to_change
    return result
