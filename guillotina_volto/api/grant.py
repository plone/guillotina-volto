from guillotina import configure
from guillotina.interfaces import IResource
from guillotina.interfaces import IInheritPermissionManager
from guillotina.interfaces import IPrincipalRoleManager

from guillotina.interfaces import IInheritPermissionMap
from guillotina.interfaces import IPrincipalRoleMap
from guillotina.exceptions import ContainerNotFound
from guillotina.interfaces.catalog import ICatalogUtility

from guillotina.utils import get_current_container
from guillotina.interfaces import IRole
from guillotina.auth.role import local_roles
from guillotina import app_settings
from guillotina.component import get_utility
from guillotina.component import query_utility
from copy import deepcopy


PERMISSIONS_TO_FORBIT_ONINHERIT = [
    "guillotina.ViewContent",
    "guillotina.ModifyContent",
    "guillotina.DeleteContent",
    "guillotina.AddContent",
    "guillotina.AccessContent",
]


@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.SeePermissions",
    name="@grant",
)
async def grantinfo_get(context, request):
    """ principals -> roles """
    search = request.query.get("search")
    if search is not None:
        search = search.lower()

    result = {"available_roles": [], "entries": []}

    # Inherit
    inheritMap = IInheritPermissionMap(context)
    permissions = inheritMap.get_locked_permissions()
    if len(permissions) > 0:
        result["inherit"] = False
    else:
        result["inherit"] = True

    # Roles
    roles = local_roles()
    valid_roles = [
        role for role in roles if role in app_settings.get("available_roles", [])
    ]
    for role in valid_roles:
        role_obj = get_utility(IRole, name=role)
        result["available_roles"].append(
            {"id": role, "title": role_obj.title, "description": role_obj.description}
        )

    prinrole = IPrincipalRoleMap(context)
    settings = [
        setting
        for setting in prinrole.get_principals_and_roles()
        if setting[0] in valid_roles
    ]
    valid_settings = {}
    default_roles = {role: None for role in valid_roles}

    try:
        container = get_current_container()
        users = await container.async_get("users")
        groups = await container.async_get("groups")
    except (AttributeError, KeyError, ContainerNotFound):
        return None

    for data in settings:
        if data[1] not in valid_settings:
            user = await users.async_get(data[1])
            if user:
                valid_settings[data[1]] = {
                    "id": data[1],
                    "disabled": user.disabled,
                    "login": None,
                    "roles": deepcopy(default_roles),
                    "title": user.name,
                    "type": "user",
                    "origin": "dbusers",
                }
            else:
                group = await groups.async_get(data[1])
                if group:
                    valid_settings[data[1]] = {
                        "id": data[1],
                        "disabled": group.disabled,
                        "login": None,
                        "roles": deepcopy(default_roles),
                        "title": group.name,
                        "type": "group",
                        "origin": "dbusers",
                    }
                else:
                    valid_settings[data[1]] = {
                        "id": data[1],
                        "disabled": False,
                        "login": None,
                        "roles": deepcopy(default_roles),
                        "title": data[1],
                        "type": "user",
                        "origin": "system",
                    }
        valid_settings[data[1]]["roles"].update({data[0]: data[2]})

    result["entries"] = list(valid_settings.values())

    if search is not None:
        catalog = query_utility(ICatalogUtility)
        query_result = await catalog.search(container, {"type_name": ["User", "Group"]})
        for obj in query_result["items"]:
            ident = obj.get("id", "")
            if search in ident.lower() and ident not in valid_settings:
                result["entries"].append(
                    {
                        "id": ident,
                        "disabled": False,
                        "login": None,
                        "roles": deepcopy(default_roles),
                        "title": obj.get("title", ""),
                        "type": obj.get("type_name").lower(),
                    }
                )

    return result


@configure.service(
    context=IResource,
    method="POST",
    permission="guillotina.ChangePermissions",
    name="@grant",
)
async def grantinfo_post(context, request):
    payload = await request.json()
    inherit = payload.get("inherit", None)

    inheritManager = IInheritPermissionManager(context)
    if inherit is True:
        for permission in PERMISSIONS_TO_FORBIT_ONINHERIT:
            inheritManager.allow_inheritance(permission)
    elif inherit is False:
        for permission in PERMISSIONS_TO_FORBIT_ONINHERIT:
            inheritManager.deny_inheritance(permission)

    entries = payload.get("entries", [])
    try:
        container = get_current_container()
        users = await container.async_get("users")
        groups = await container.async_get("groups")
    except (AttributeError, KeyError, ContainerNotFound):
        return None

    prinrole = IPrincipalRoleManager(context)
    for entry in entries:
        valid = False
        if entry["type"] == "group" and await groups.async_contains(entry["id"]):
            valid = True
        if entry["type"] == "user" and await users.async_contains(entry["id"]):
            valid = True

        if valid:
            for role, permission in entry["roles"].items():
                if permission == "Allow":
                    prinrole.assign_role_to_principal(entry["id"], role)
                elif permission == "Deny":
                    prinrole.remove_role_from_principal(entry["id"], role)
                elif permission is None:
                    prinrole.unset_role_for_principal(entry["id"], role)
                elif permission == "AllowSingle":
                    prinrole.assign_role_to_principal_no_inherit(entry["id"], role)
