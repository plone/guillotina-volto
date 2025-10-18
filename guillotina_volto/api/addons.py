from guillotina import addons
from guillotina import app_settings
from guillotina import configure
from guillotina import error_reasons
from guillotina.i18n import MessageFactory
from guillotina.interfaces import IAddons
from guillotina.response import ErrorResponse
from guillotina.utils import get_registry

from guillotina_volto.interfaces.content import ISite


_ = MessageFactory("guillotina")


@configure.service(
    context=ISite,
    method="GET",
    permission="guillotina.ManageAddons",
    name="@addons",
    summary="List available addons",
    responses={
        "200": {
            "description": "Get list of available and installed addons",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AddonResponse"}}},
        }
    },
)
async def get_addons(context, request):
    result = {"items": []}
    for key, addon in app_settings["available_addons"].items():
        result["items"].append(
            {
                "id": key,
                "title": addon["title"],
                "dependencies": addon["dependencies"],
                "is_installed": False,
                "upgrade_info": {"available": False},
            }
        )

    registry = await get_registry()
    config = registry.for_interface(IAddons)

    for installed in config["enabled"]:
        for addon in result["items"]:
            if addon["id"] == installed:
                addon["is_installed"] = True
    return result


@configure.service(
    context=ISite,
    method="POST",
    permission="guillotina.ManageAddons",
    name="@addons/{id_to_install}/install",
    summary="List available addons",
    responses={
        "200": {
            "description": "Install a given addon",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AddonResponse"}}},
        }
    },
)
async def install_addon(context, request):
    id_to_install = request.matchdict["id_to_install"]
    if id_to_install not in app_settings["available_addons"]:
        return ErrorResponse(
            "RequiredParam",
            _("Property 'id' is required to be valid"),
            status=412,
            reason=error_reasons.INVALID_ID,
        )

    registry = await get_registry()
    config = registry.for_interface(IAddons)

    if id_to_install in config["enabled"]:
        return ErrorResponse(
            "Duplicate", _("Addon already installed"), status=412, reason=error_reasons.ALREADY_INSTALLED
        )

    await addons.install(context, id_to_install)
    return await get_addons(context, request)
