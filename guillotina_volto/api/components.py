from guillotina import configure
from guillotina.api.service import Service
from guillotina.component import get_multi_adapter
from guillotina.event import notify
from guillotina.events import ObjectVisitedEvent
from guillotina.interfaces import IAbsoluteURL
from guillotina.interfaces import IResource
from guillotina.interfaces import IResourceSerializeToJson
from guillotina.utils import find_container
from guillotina.utils import get_content_depth
from guillotina.utils import get_current_container
from guillotina.utils import get_object_url

from guillotina_volto.interfaces import ICMSLayer
from guillotina_volto.interfaces import ISite
from guillotina_volto.utils import get_search_utility


@configure.service(
    context=IResource,
    method="GET",
    layer=ICMSLayer,
    permission="guillotina.AccessContent",
    name="@breadcrumbs",
    summary="Components for a bredcrumbs",
    responses={
        "200": {
            "description": "Result results on breadcrumbs",
            "schema": {
                "type": "object",
                "properties": {
                    "@id": "string",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "@id": {"type": "string"},
                                "title": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }
    },
)
class Breadcrumbs(Service):
    async def __call__(self):
        result = []
        context = self.context
        while context is not None and not ISite.providedBy(context):
            result.append({"title": context.title, "@id": IAbsoluteURL(context, self.request)()})
            context = getattr(context, "__parent__", None)
        result.reverse()

        return {"@id": self.request.url, "items": result}


def recursive_fill(mother_list, pending_dict):
    for element in mother_list:
        if element["@name"] in pending_dict:
            element["items"] = pending_dict[element["@name"]]
            recursive_fill(element["items"], pending_dict)


@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.AccessContent",
    name="@navigation",
    summary="Navigation view",
    responses={
        "200": {
            "description": "Result results on navigation",
            "schema": {
                "type": "object",
                "properties": {
                    "@id": "string",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "@id": {"type": "string"},
                                "title": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }
    },
)
class Navigation(Service):
    async def __call__(self):
        search = get_search_utility()
        container = find_container(self.context)
        depth = get_content_depth(container)
        max_depth = None
        if "expand.navigation.depth" in self.request.query:
            max_depth = str(int(self.request.query["expand.navigation.depth"]) + depth)
            depth_query = {"depth__gte": depth, "depth__lte": max_depth}
        else:
            depth_query = {"depth": depth}

        depth_query["hidden_navigation"] = False
        result = await search.search(
            container,
            {**{"_sort_asc": "position_in_parent", "_size": 100}, **depth_query},
        )

        pending_dict = {}
        for brain in result["items"]:
            brain_serialization = {
                "title": brain.get("title"),
                "@id": brain.get("@id"),
                "@name": brain.get("uuid"),
                "description": "",
            }
            pending_dict.setdefault(brain.get("parent_uuid"), []).append(brain_serialization)

        parent_uuid = container.uuid
        if parent_uuid not in pending_dict:
            final_list = []
        else:
            final_list = pending_dict[parent_uuid]
        if max_depth is not None:
            recursive_fill(final_list, pending_dict)

        return {"@id": self.request.url, "items": final_list}


@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.AccessContent",
    name="@actions",
    summary="Actions view",
    responses={
        "200": {
            "description": "Result results on actions",
            "schema": {"properties": {}},
        }
    },
)
class Actions(Service):
    async def __call__(self):
        return {
            "object": [
                {"id": "view", "title": "View", "url": None},
                {"id": "add", "title": "Add", "url": None},
                {"icon": "toolbar-action/edit", "id": "edit", "title": "Edit", "url": None},
                {"id": "folderContents", "title": "Contents", "url": None},
                {"id": "history", "title": "History", "url": None},
                {"id": "contentrules", "title": "Rules", "url": None},
                {"id": "local_roles", "title": "Sharing", "url": None},
            ],
            "object_buttons": [
                {"id": "cut", "title": "Cut", "url": None},
                {"id": "copy", "title": "Copy", "url": None},
                {"id": "paste", "title": "Paste", "url": None},
                {"id": "delete", "title": "Delete", "url": None},
                {"id": "rename", "title": "Rename", "url": None},
            ],
            "site_actions": [
                {"id": "sitemap", "title": "Sitemap", "url": None},
                {"id": "accessibility", "title": "Accessibility", "url": None},
                {"id": "contact", "title": "Contact", "url": None},
            ],
            "user": [
                {"id": "preferences", "title": "Preferences", "url": None},
                {"id": "plone_setup", "title": "Site Setup", "url": None},
                {"id": "logout", "title": "Log out", "url": None},
            ],
        }


@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.AccessContent",
    name="@navroot",
    summary="Navigation view",
    responses={
        "200": {
            "description": "Result results on navigation",
            "schema": {
                "type": "object",
                "properties": {
                    "@id": "string",
                    "navroot": "object"
                },
            },
        }
    },
)
class Navroot(Service):
    async def __call__(self):
        full_url = get_object_url(self.context)
        container = get_current_container()
        serializer = get_multi_adapter((container, self.request), IResourceSerializeToJson)
        include = omit = []
        if self.request.query.get("include"):
            include = self.request.query.get("include").split(",")
        if self.request.query.get("omit"):
            omit = self.request.query.get("omit").split(",")
        try:
            result = await serializer(include=include, omit=omit)
        except TypeError:
            result = await serializer()
        return {"@id": f"{full_url}/@navroot", "navroot": result}
