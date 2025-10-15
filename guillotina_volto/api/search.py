from guillotina import configure
from guillotina.api.search import QUERY_PARAMETERS
from guillotina.api.search import search_get
from guillotina.interfaces import IResource


@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.SearchContent",
    name="@search",
    validate=True,
    parameters=QUERY_PARAMETERS,
    summary="Make search request",
    responses={
        "200": {
            "description": "Search results",
            "content": {
                "application/json": {"schema": {"type": "object", "$ref": "#/components/schemas/SearchResults"}}
            },
        }
    },
)
async def volto_search_get(context, request):
    data = await search_get(context, request)
    for item in data["items"]:
        item["@type"] = item.get("type_name", None)
        item["UID"] = item.get("uuid", None)

    return data
