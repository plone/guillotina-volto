import json
import pytest
import os

pytestmark = pytest.mark.asyncio

NOT_POSTGRES = os.environ.get("DATABASE", "DUMMY") in ("cockroachdb", "DUMMY")
PG_CATALOG_SETTINGS = {
    "applications": ["guillotina.contrib.catalog.pg"],
    "load_utilities": {
        "catalog": {
            "provides": "guillotina.interfaces.ICatalogUtility",
            "factory": "guillotina.contrib.catalog.pg.utility.PGSearchUtility",
        }
    },
}

@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_navigation(cms_requester):
    async with cms_requester as requester:
        resp, status = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps({"@type": "CMSFolder", "id": "folder1"}),
        )
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1",
            data=json.dumps({"@type": "Document", "id": "doc1"}),
        )
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1",
            data=json.dumps({"@type": "Document", "id": "doc2"}),
        )

        resp, status = await requester(
            "GET", "/db/guillotina/@navigation?expand.navigation.depth=2"
        )

        assert len(resp["items"][0]["items"]) == 2
