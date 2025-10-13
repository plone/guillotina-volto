from guillotina import configure
from guillotina.api.content import DefaultGET
from guillotina.api.service import Service
from guillotina.interfaces import IAbsoluteURL
from guillotina.interfaces import IResource
from guillotina.utils import find_container
from guillotina.utils import get_content_depth
from guillotina.utils import get_current_container
from guillotina.utils import get_object_url

from guillotina_volto.contrib.language.interfaces import ILanguageFolder
from guillotina_volto.interfaces import ICMSLayer
from guillotina_volto.interfaces import ISite
from guillotina_volto.utils import get_parent_by_interface
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
        context_to_search = container
        parent_language_folder = get_parent_by_interface(self.context, ILanguageFolder)
        if parent_language_folder is not None:
            context_to_search = parent_language_folder
        depth = get_content_depth(context_to_search)
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

        parent_uuid = context_to_search.uuid
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
                {
                    "icon": "toolbar-action/edit",
                    "id": "edit",
                    "title": "Edit",
                    "url": None,
                },
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
                "properties": {"@id": "string", "navroot": "object"},
            },
        }
    },
)
class Navroot(Service):
    async def __call__(self):
        language_folder = get_parent_by_interface(self.context, ILanguageFolder)
        if language_folder is None:
            container = get_current_container()
            self.context = container
        else:
            self.context = language_folder
        # We can not do super().__call__() since DefaultGETResource
        # does that already
        full_response = await DefaultGET.__call__(self)
        full_url = get_object_url(self.context)
        return {"@id": f"{full_url}/@navroot", "navroot": full_response}
