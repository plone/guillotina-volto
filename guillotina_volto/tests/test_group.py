import pytest
import json
import asyncio
from guillotina.tests.test_catalog import PG_CATALOG_SETTINGS, NOT_POSTGRES

pytestmark = pytest.mark.asyncio


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_groups(cms_requester):
    requester = cms_requester
    resp, status = await requester("GET", "/db/guillotina/@groups")
    assert status == 200
    assert len(resp) == 1
    _group = {
        "@type": "Group",
        "id": "test_group",
        "title": "Test Group",
        "groupname": "Test Group",
        "description": "Test Group Description",
    }
    resp, status_code = await requester("POST", "/db/guillotina/@groups", data=json.dumps(_group))
    assert status_code == 200
    resp, status = await requester("GET", "/db/guillotina/@groups")
    assert status == 200
    assert len(resp) == 2