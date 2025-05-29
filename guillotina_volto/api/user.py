from guillotina import configure
from guillotina.api.service import Service
from guillotina_volto.interfaces import ISite
from guillotina.response import ErrorResponse
from guillotina.content import create_content_in_container
from guillotina.utils import get_current_request
from guillotina.event import notify
from guillotina.events import ObjectAddedEvent


@configure.service(
    context=ISite,
    name="@users",
    permission="guillotina.ManageUsers",
    summary="Get available roles on guillotina container",
    method="POST",
    responses={
        "200": {
            "description": "Create a new user",
            "content": {"application/json": {"schema": {"type": "array"}}},
        }
    },
)
class CreateUser(Service):
    async def __call__(self):
        users_folder = await self.context.async_get("users", None)
        request = get_current_request()
        payload = await request.json()
        if users_folder is None:
            raise ErrorResponse("Users not found", status=412)
        payload_user = {}
        try:
            payload_user["email"] = payload["email"]
            payload_user["username"] = payload["username"]
            payload_user["name"] = payload.get("name", "")
            payload_user["password"] = payload["password"]
            payload_user["user_groups"] = payload.get("user_groups", [])
            payload_user["user_roles"] = payload.get("user_roles", [])
            payload_user["user_permissions"] = payload.get("user_permissions", [])
        except KeyError:
            raise ErrorResponse("Wrong key", status=412)
        user_obj = await create_content_in_container(
            users_folder, "User",
            id_=payload["username"],
            **payload_user
        )
        await notify(ObjectAddedEvent(user_obj, users_folder, payload=payload_user))
