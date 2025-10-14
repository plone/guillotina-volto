from guillotina import configure
from guillotina.api.service import Service
from guillotina.component import get_multi_adapter
from guillotina.interfaces import ISchemaFieldSerializeToJson
from guillotina.schema import get_fields_in_order
from guillotina.schema.vocabulary import VocabularyRegistryError
from guillotina.schema.vocabulary import getVocabularyRegistry
from guillotina.utils import resolve_dotted_name

from guillotina_volto.interfaces.content import ISite


@configure.service(
    context=ISite,
    method="GET",
    permission="guillotina.ManageUsers",
    name="@userschema",
    summary="List users schema",
    responses={
        "200": {
            "description": "Get information of the users schema",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AddonResponse"}}},
        }
    },
)
async def get_users_schema(context, request):
    schema_name = "guillotina.contrib.dbusers.content.users.IUser"
    schema = {"properties": {}, "fieldsets": [], "required": []}
    iface = resolve_dotted_name(schema_name)
    fields = []
    all_names = []
    fields_allowed = [
        "username",
        "email",
        "password",
        "user_groups",
        "user_roles",
        "user_permissions",
        "name",
        "disabled",
    ]
    for name, field in get_fields_in_order(iface):
        all_names.append(name)
        if name not in fields_allowed:
            continue
        if field.required:
            schema["required"].append(name)
        serializer = get_multi_adapter((field, iface, request), ISchemaFieldSerializeToJson)
        schema["properties"][name] = await serializer()
        fields.append(name)
    schema["fieldsets"] = [{"fields": fields, "id": "default", "title": "default"}]
    return schema


@configure.service(
    context=ISite,
    method="GET",
    permission="guillotina.AccessContent",
    name="@querystring",
    summary="The `@querystring` endpoint returns the querystring config.",
    responses={
        "200": {
            "@id": "Get information of the users schema",
            "indexes": {},
            "sortable_indexes": {},
        }
    },
)
class QuerystringGET(Service):
    data = [
        {
            "name": "path",
            "type": "path",
            "attr": "path",
            "title": "Location",
            "description": "The location of an item",
            "group": "Metadata",
            "enabled": True,
            "sortable": False,
            "operators": {
                "string.absolutePath": {
                    "title": "Absolute path",
                    "description": "Location in the site structure",
                    "operation": "absolutePath",
                    "widget": "ReferenceWidget",
                },
                "string.path": {
                    "title": "Navigation path",
                    "description": "Location in the navigation structure",
                    "operation": "navigationPath",
                    "widget": "ReferenceWidget",
                },
                "string.relativePath": {
                    "title": "Relative path",
                    "description": "Use '../' to navigate to parent objects.",
                    "operation": "relativePath",
                    "widget": "RelativePathWidget",
                },
            },
            "vocabulary": None,
        },
        {
            "name": "title",
            "type": "text",
            "attr": "title",
            "title": "Title",
            "description": "An item's title",
            "group": "Text",
            "enabled": True,
            "sortable": True,
            "operators": {
                "string.contains": {
                    "title": "Contains",
                    "description": "",
                    "operation": "contains",
                    "widget": "StringWidget",
                }
            },
            "vocabulary": None,
        },
        {
            "name": "id",
            "type": "string",
            "attr": "id",
            "title": "Short name (id)",
            "description": "The short name of an item (used in the url)",
            "group": "Metadata",
            "enabled": True,
            "sortable": True,
            "operators": {
                "string.is": {
                    "title": "Is",
                    "description": "Tip: you can use * to autocomplete.",
                    "operation": "equal",
                    "widget": "StringWidget",
                }
            },
            "vocabulary": None,
        },
        {
            "name": "creators",
            "type": "string",
            "attr": "creators",
            "title": "Creator",
            "description": "The person that created an item",
            "group": "Metadata",
            "enabled": True,
            "sortable": True,
            "operators": {
                "selection.any": {
                    "title": "Matches any of",
                    "description": "Tip: you can use * to autocomplete.",
                    "operation": "contains",
                    "widget": "MultipleSelectionWidget",
                },
                "string.currentUser": {
                    "title": "Current logged in user",
                    "description": "The user viewing the querystring results",
                    "operation": "currentUser",
                    "widget": None,
                },
            },
            "vocabulary": "users",
        },
        {
            "name": "creation_date",
            "type": "date",
            "attr": "creation_date",
            "title": "Creation date",
            "description": "The date an item was created",
            "group": "Dates",
            "enabled": True,
            "sortable": True,
            "operators": {
                # "date.afterRelativeDate": {
                #     "title": "After relative Date",
                #     "description": "After N days in the future",
                #     "operation": "afterRelativeDate",
                #     "widget": "RelativeDateWidget",
                # },
                # "date.afterToday": {
                #     "title": "After today",
                #     "description": "After the current day",
                #     "operation": "afterToday",
                #     "widget": None,
                # },
                # "date.beforeRelativeDate": {
                #     "title": "Before relative Date",
                #     "description": "Before N days in the past",
                #     "operation": "beforeRelativeDate",
                #     "widget": "RelativeDateWidget",
                # },
                # "date.beforeToday": {
                #     "title": "Before today",
                #     "description": "Before the current day",
                #     "operation": "beforeToday",
                #     "widget": None,
                # },
                "date.between": {
                    "title": "Between dates",
                    "description": "Please use YYYY/MM/DD.",
                    "operation": "between",
                    "widget": "DateRangeWidget",
                },
                "date.largerThan": {
                    "title": "After date",
                    "description": "Please use YYYY/MM/DD.",
                    "operation": "largerThan",
                    "widget": "DateWidget",
                },
                # "date.largerThanRelativeDate": {
                #     "title": "Within last",
                #     "description": "Please enter the number in days.",
                #     "operation": "moreThanRelativeDate",
                #     "widget": "RelativeDateWidget",
                # },
                "date.lessThan": {
                    "title": "Before date",
                    "description": "Please use YYYY/MM/DD.",
                    "operation": "lessThan",
                    "widget": "DateWidget",
                },
                # "date.lessThanRelativeDate": {
                #     "title": "Within next",
                #     "description": "Please enter the number in days.",
                #     "operation": "lessThanRelativeDate",
                #     "widget": "RelativeDateWidget",
                # },
                "date.today": {
                    "title": "Today",
                    "description": "The current day",
                    "operation": "today",
                    "widget": None,
                },
            },
            "vocabulary": None,
        },
        {
            "name": "type_name",
            "type": "string",
            "attr": "type_name",
            "title": "Type",
            "description": "An item's type (e.g. Event)",
            "group": "Metadata",
            "enabled": True,
            "sortable": False,
            "operators": {
                "selection.any": {
                    "title": "Matches any of",
                    "description": "Tip: you can use * to autocomplete.",
                    "operation": "contains",
                    "widget": "MultipleSelectionWidget",
                }
            },
            "vocabulary": "content_types",
        },
        {
            "name": "review_state",
            "type": "string",
            "attr": "review_state",
            "title": "Review state",
            "description": "An item's workflow state (e.g.published)",
            "group": "Metadata",
            "enabled": True,
            "sortable": True,
            "operators": {
                "selection.any": {
                    "title": "Matches any of",
                    "description": "Tip: you can use * to autocomplete.",
                    "operation": "contains",
                    "widget": "MultipleSelectionWidget",
                }
            },
            "vocabulary": "workflow_states",
        },
    ]

    def get_enabled_indexes(self):
        def is_enabled(item):
            return item["enabled"]

        result = {}
        for value in map(self.data_to_json, filter(is_enabled, self.data)):
            result[value["name"]] = value
        return result

    def get_sortable_indexes(self):
        def is_sortable(item):
            return item["sortable"]

        result = {}
        for value in map(self.data_to_json, filter(is_sortable, self.data)):
            result[value["name"]] = value
        return result

    def data_to_json(self, item):
        if "vocabulary" in item:
            vocabulary_registry = getVocabularyRegistry()
            try:
                vocab = vocabulary_registry.get(self.context, item["vocabulary"])
                item["values"] = {}
                for term in vocab.keys():
                    new_title = vocab.getTerm(term)
                    item["values"][term] = {"title": new_title}
            except VocabularyRegistryError:
                pass

        item["operations"] = item["operators"].keys()
        return item

    async def __call__(self):
        return {
            "@id": self.request.url,
            "indexes": self.get_enabled_indexes(),
            "sortable_indexes": self.get_sortable_indexes(),
        }
