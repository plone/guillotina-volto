import pytest


pytestmark = pytest.mark.asyncio


async def test_menu_definition(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "GET",
        "/db/guillotina/@sharing",
    )
    assert status == 200
    assert len(resp["available_roles"]) > 0
