from guillotina import configure
from guillotina.component import getMultiAdapter
from guillotina.interfaces import IAbsoluteURL
from guillotina.interfaces import IResource
from guillotina.utils import get_behavior
from guillotina.utils import get_current_container
from guillotina.response import HTTPBadRequest

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
    container = get_current_container()
    payload = await request.json()
    if "version" not in payload:
        raise HTTPBadRequest(content={"message": "Needs to pass version"})
    version = payload["version"]
    final_values = {}
    for key, value in reversed(list(bhr.history.items())):
        if key == version:
            # Apply changes here
            pass
        else:
            # calculate values here
            pass
