from guillotina import configure
from guillotina.api.service import Service
from guillotina.component import getMultiAdapter
from guillotina.interfaces import IAbsoluteURL

from guillotina_volto.interfaces import ISite


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
        app_roles = configure.get_configurations("guillotina_volto", "role")
        for _type, role_config in app_roles:
            role_id = role_config["config"].get("id")
            role_title = role_config["config"].get("title")
            result.append(
                {
                    "@id": f"{url}/@roles/{role_id}",
                    "@type": "role",
                    "id": role_id,
                    "title": role_title,
                }
            )
        return result
