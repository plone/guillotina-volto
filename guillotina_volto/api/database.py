from urllib.parse import urlparse
from urllib.parse import urlunparse

from guillotina import app_settings
from guillotina import configure
from guillotina.utils import get_current_db
from guillotina.utils import get_object_url

from guillotina_volto.interfaces.content import ISite


def mask_dsn(dsn: str, placeholder: str = "***") -> str:
    """
    Return the same DSN but with the password replaced by `placeholder`.
    """
    p = urlparse(dsn)
    # p.username and p.password may be None if they’re missing
    netloc = p.hostname or ""
    if p.username:
        userinfo = f"{p.username}:{placeholder}"
        netloc = f"{userinfo}@{netloc}"
    if p.port:
        netloc = f"{netloc}:{p.port}"

    return urlunparse((p.scheme, netloc, p.path, "", "", ""))


@configure.service(
    context=ISite,
    method="GET",
    permission="guillotina.GetDatabases",
    name="@database",
    summary="Gives information about the database",
    responses={
        "200": {
            "description": "Get list of available and installed addons",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AddonResponse"}}},
        }
    },
)
async def get_database(context, request):
    db = get_current_db()
    results = {
        "db_name": None,
        "database_size": None,
        "db_size": None,
        "cache_size": None,
        "cache_length": None,
        "cache_length_bytes": None,
        "cache_detail_length": [],
    }
    path = get_object_url(context)
    for database_name, database_payload in app_settings["databases"].items():
        if database_name == db.id:
            results["db_name"] = mask_dsn(database_payload["dsn"])
    results["@id"] = f"{path}/@database"
    return results
