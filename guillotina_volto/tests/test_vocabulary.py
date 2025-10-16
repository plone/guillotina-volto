import pytest
from guillotina.tests.test_catalog import NOT_POSTGRES


pytestmark = pytest.mark.asyncio


@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_vocabulary(cms_requester):
    resp, status = await cms_requester(
        "GET", "/db/guillotina/@vocabularies/content_types"
    )
    assert status == 200
    assert "Page" in list(map(lambda x: x["title"], resp["items"]))
    assert resp["items_total"] == 8

    resp, status = await cms_requester(
        "GET", "/db/guillotina/@vocabularies/workflow_states"
    )
    assert status == 200
    assert "Private" in list(map(lambda x: x["title"], resp["items"]))
    assert resp["items_total"] == 2
