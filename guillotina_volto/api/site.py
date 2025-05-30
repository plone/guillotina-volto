from guillotina import configure
from guillotina_volto.interfaces.content import ISite
from guillotina.utils import resolve_dotted_name
from guillotina.schema import get_fields_in_order
from guillotina.interfaces import ISchemaFieldSerializeToJson
from guillotina.component import get_multi_adapter


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
        "disabled"
    ]
    for name, field in get_fields_in_order(iface):
        all_names.append(name)
        if name not in fields_allowed:
            continue
        if field.required:
            schema["required"].append(name)
        serializer = get_multi_adapter(
            (field, iface, request), ISchemaFieldSerializeToJson
        )
        schema["properties"][name] = await serializer()
        fields.append(name)
    schema["fieldsets"] = [{"fields": fields, "id": "default", "title": "default"}]
    return schema
