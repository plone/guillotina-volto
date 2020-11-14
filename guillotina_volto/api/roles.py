from guillotina import configure
from guillotina.api.service import Service
from guillotina.auth.role import global_roles
from guillotina.auth.role import local_roles
from guillotina_volto.interfaces import ISite
from guillotina.interfaces import IAbsoluteURL
from guillotina.interfaces import IRole
from guillotina.component import get_utility
from guillotina.component import getMultiAdapter


@configure.service(
    context=ISite,
    name="@roles",
    permission="guillotina.ManageUsers",
    summary="Get available roles on guillotina container",
    method="GET",
    responses={
        "200": {
            "description": "List of available roles",
            "content": {"application/json": {"schema": {"type": "array"}}},
        }
    },
)
class AvailableRoles(Service):
    async def __call__(self):
        url = getMultiAdapter((self.context, self.request), IAbsoluteURL)()
        result = []
        roles = global_roles()
        for role in roles:
            role_obj = get_utility(IRole, name=role)
            result.append({
                "@id": f"{url}/@roles/{role}",
                "@type": "role",
                "id": role,
                "title": role_obj.title
            })
        return result
