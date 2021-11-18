import json

import pytest
from guillotina import testing


def base_settings_configurator(settings):
    if "applications" in settings:
        settings["applications"].append("guillotina_volto")
    else:
        settings["applications"] = ["guillotina_volto"]
    settings["container_types"] = ["Site"]


testing.configure_with(base_settings_configurator)


class CMSRequester:
    def __init__(self, guillotina, install=None):
        self.guillotina = guillotina
        self.install = install or ["cms", "dbusers", "email_validation"]
        self.requester = None

    async def get_requester(self):
        return self.guillotina

    async def __aenter__(self):
        self.requester = await self.get_requester()
        resp, status = await self.requester(
            "POST",
            "/db",
            data=json.dumps(
                {
                    "@type": "Site",
                    "title": "Guillotina Volto Site",
                    "id": "guillotina",
                    "description": "Description Guillotina Container",
                }
            ),
        )
        assert status == 200
        for addon in self.install:
            await self.requester(
                "POST", "/db/guillotina/@addons", data=json.dumps({"id": addon})
            )
        return self.requester

    async def __aexit__(self, exc_type, exc, tb):
        _, status = await self.requester("DELETE", "/db/guillotina")
        assert status in (200, 404)
        await self.guillotina.close()


@pytest.fixture(scope="function")
async def cms_requester(guillotina):
    yield CMSRequester(guillotina)
