import pytest
from guillotina.tests.test_catalog import NOT_POSTGRES


pytestmark = pytest.mark.asyncio


async def test_component(cms_requester):
    response, status = await cms_requester("GET", "/db/guillotina")
    assert status == 200
    assert "@components" in response
    response, status = await cms_requester(
        "GET", "/db/guillotina/?expand=actions,breadcrumbs,types&expand.navigation.depth=1"
    )
    assert len(response["@components"]["actions"]["object"]) > 0


@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_get_database(cms_requester):
    response, status = await cms_requester("GET", "/db/guillotina/@database")
    assert status == 200
