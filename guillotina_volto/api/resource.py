import datetime

from guillotina import configure
from guillotina.api.content import DefaultGET
from guillotina.api.service import Service
from guillotina.catalog.utils import iter_indexes
from guillotina.interfaces import IResource
from guillotina.utils import get_current_request
from guillotina.utils import get_object_url

from guillotina_volto.api.components import Actions
from guillotina_volto.api.components import Breadcrumbs
from guillotina_volto.api.components import Navigation
from guillotina_volto.api.components import Navroot
from guillotina_volto.api.types import Types
from guillotina_volto.contrib.language.api import GetTranslations
from guillotina_volto.contrib.language.interfaces import ILanguageFolder
from guillotina_volto.utils import Search
from guillotina_volto.utils import get_parent_by_interface


@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.AccessContent",
    summary="Includes all the necessary information by volto",
    responses={
        "200": {
            "description": "Serialization",
            "schema": {"properties": {}},
        }
    },
)
class DefaultGETResource(DefaultGET):
    async def __call__(self):
        mapping_expansions = {
            "actions": {"class": Actions, "root": False, "component": True},
            "breadcrumbs": {"class": Breadcrumbs, "root": False, "component": True},
            "navigation": {"class": Navigation, "root": False, "component": True},
            "types": {"class": Types, "root": False, "component": True},
            "translations": {
                "class": GetTranslations,
                "root": False,
                "component": True,
            },
            "navroot": {"class": Navroot, "root": False, "component": True},
        }
        full_response = await super().__call__()
        full_url = get_object_url(self.context)
        request = get_current_request()
        expansions = request.query.get("expand", [])
        if expansions:
            expansions = expansions.split(",")
        components = {
            "actions": {"@id": f"{full_url}/@actions"},
            "aliases": {"@id": f"{full_url}/@aliases"},
            "breadcrumbs": {"@id": f"{full_url}/@breadcrumbs"},
            "contextnavigation": {"@id": f"{full_url}/@contextnavigation"},
            "navigation": {"@id": f"{full_url}/@navigation"},
            "navroot": {"@id": f"{full_url}/@navroot"},
            "types": {"@id": f"{full_url}/@types"},
            "workflow": {"@id": f"{full_url}/@workflow"},
            "translations": {"@id": f"{full_url}/@translations"},
        }
        parent_language_folder = get_parent_by_interface(self.context, ILanguageFolder)
        if parent_language_folder:
            full_response["language"] = {
                "title": parent_language_folder.title.upper(),
                "token": parent_language_folder.id,
            }
        for expand in expansions:
            mapping_payload = mapping_expansions.get(expand, None)
            if mapping_payload is None:
                continue
            mapping_class = mapping_payload.get("class", None)
            if mapping_class:
                response = await mapping_class.__call__(self)
                if "@id" in response:
                    response["@id"] = f"{full_url}/@{expand}"
                if mapping_payload.get("component") is True:
                    components[expand] = response
                elif mapping_payload.get("root") is True:
                    full_response[expand] = response
        full_response["@components"] = components
        return full_response


@configure.service(
    context=IResource,
    method="POST",
    permission="guillotina.AccessContent",
    name="@querystring-search",
    summary="The `@querystring` endpoint returns the querystring config.",
    responses={
        "200": {
            "@id": "Get information of the users schema",
            "indexes": {},
            "sortable_indexes": {},
        }
    },
)
class QuerystringSearchPOST(Service):
    async def __call__(self):
        payload = await self.request.json()
        utility = Search(self.context)
        query = {}

        if "sort_on" in payload:
            if payload["sort_order"] == "ascending":
                query["_sort_asc"] = payload["sort_on"]
            else:
                query["_sort_des"] = payload["sort_on"]

        if "b_size" in payload:
            query["_size"] = payload["b_size"]
        if "b_start" in payload:
            query["_from"] = payload["b_start"]

        if "limit" in payload:
            # TODO: implement the custom limit
            pass

        if "query" in payload:
            for item_query in payload["query"]:
                field = item_query["i"]
                operation = item_query["o"]
                value = item_query["v"]

                if field == "SearchableText":
                    oring = {}
                    for index_name, idx_data in iter_indexes():
                        if idx_data["type"] in ("text", "searchabletext"):
                            oring["{}__in".format(index_name)] = value
                    query["__or"] = oring
                elif operation == "string.absolutePath":
                    query["path"] = value
                elif operation == "string.relativePath":
                    query["path__in"] = value
                elif operation == "string.contains":
                    query[f"{field}__in"] = value
                elif operation == "date.today":
                    query[field] = datetime.date.today()
                elif operation == "date.between":
                    query[f"{field}_gte"] = value[0]
                    query[f"{field}__lte"] = value[1]
                elif operation == "date.largerThan":
                    query[f"{field}__gte"] = value
                elif operation == "date.lessThan":
                    query[f"{field}__lte"] = value
                elif operation == "selection.any":
                    query[f"{field}__in"] = ",".join(value)

        results = await utility.search_raw(query=query)

        return {"@id": self.request.url, "items": results["items"], "items_total": results["items_total"]}
