import json
import os

import pytest_asyncio
from async_asgi_testclient import TestClient
from guillotina import testing
from guillotina.component import get_utility
from guillotina.component import globalregistry
from guillotina.factory import make_app
from guillotina.interfaces import IApplication
from guillotina.tests.fixtures import GuillotinaDBAsgiRequester
from guillotina.tests.fixtures import _clear_dbs
from guillotina.tests.fixtures import clear_task_vars
from guillotina.tests.fixtures import get_db_settings


DATABASE = os.environ.get("DATABASE", "DUMMY")


def base_settings_configurator(settings):
    if "applications" in settings:
        settings["applications"].append("guillotina.contrib.workflows")
    else:
        settings["applications"] = ["guillotina.contrib.workflows"]
    settings["allow_register"] = True
    settings["container_types"] = ["Site"]
    settings["applications"].append("guillotina.contrib.workflows")
    settings["applications"].append("guillotina.contrib.vocabularies")
    settings["applications"].append("guillotina.contrib.dbusers")
    settings["applications"].append("guillotina.contrib.mailer")
    settings["applications"].append("guillotina.contrib.email_validation")
    settings["applications"].append("guillotina.contrib.catalog.pg")
    settings["applications"].append("guillotina_volto")
    settings["load_utilities"] = {
        "catalog": {
            "provides": "guillotina.interfaces.ICatalogUtility",
            "factory": "guillotina.contrib.catalog.pg.utility.PGSearchUtility",
        },
    }
    settings["auth_extractors"] = [
        "guillotina.auth.extractors.BearerAuthPolicy",
        "guillotina.auth.extractors.BasicAuthPolicy",
        "guillotina.auth.extractors.WSTokenAuthPolicy",
    ]
    settings["auth_token_validators"] = [
        "guillotina.auth.validators.SaltedHashPasswordValidator",
        "guillotina.auth.validators.JWTValidator",
    ]


testing.configure_with(base_settings_configurator)


@pytest_asyncio.fixture(scope="function")
async def app_client(event_loop, db, request):
    globalregistry.reset()
    app = make_app(settings=get_db_settings_volto(request.node), loop=event_loop)
    async with TestClient(app, timeout=90) as client:
        await _clear_dbs(app.app.root)
        yield app, client
    clear_task_vars()


def get_db_settings_volto(node):
    db_settings = get_db_settings(node)
    db_settings["storages"]["db"] = {"dsn": {"storage": "postgresql", "password": "postgres", "scheme": "postgres"}}
    if DATABASE == "postgres":
        db_settings["databases"]["db"]["dsn"]["password"] = "postgres"
        db_settings["databases"]["db-custom"]["dsn"]["password"] = "postgres"
    return db_settings


class GuillotinaVoltoDBAsgiRequester(GuillotinaDBAsgiRequester):
    def __init__(self, client):
        self.client = client
        self.root = get_utility(IApplication, name="root")
        self.db = self.root["db"]

    async def __call__(self, *args, **kwargs):
        headers = kwargs.get("headers", {})
        headers["X-Wait"] = "100"
        kwargs["headers"] = headers
        return await super().__call__(*args, **kwargs)


@pytest_asyncio.fixture(scope="function")
async def guillotina_volto_app(app_client):
    _, client = app_client
    yield GuillotinaVoltoDBAsgiRequester(client)


@pytest_asyncio.fixture(scope="function")
async def cms_requester(request, guillotina_volto_app):
    guillotina = guillotina_volto_app
    resp, status = await guillotina(
        "POST",
        "/db",
        data=json.dumps(
            {
                "@type": "Site",
                "title": "Title guillotina volto",
                "id": "guillotina",
            }
        ),
    )
    assert status == 200
    yield guillotina
