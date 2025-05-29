from guillotina import configure, app_settings
from guillotina.utils import get_registry
from guillotina.interfaces import IAddons
from guillotina_volto.interfaces.content import ISite


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
                "upgrade_info": {"available": False}
            }
        )

    registry = await get_registry()
    config = registry.for_interface(IAddons)

    for installed in config["enabled"]:
        for addon in result["items"]:
            if addon["id"] == installed:
                addon["is_installed"] = True
    return result
