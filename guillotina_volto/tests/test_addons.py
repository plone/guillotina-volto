import pytest


pytestmark = pytest.mark.asyncio


async def test_addon_get(cms_requester):
    response, status = await cms_requester("GET", "/db/guillotina/@addons")
    assert status == 200
    assert len(response["items"]) > 0
    assert response["items"][0]["is_installed"] is True


@pytest.mark.parametrize("cms_requester", [["cms", "dbusers"]], indirect=True)
async def test_addons_install(cms_requester):
    response, status = await cms_requester("GET", "/db/guillotina/@addons")
    assert status == 200
    found = False
    for addon in response["items"]:
        if addon["id"] == "email_validation":
            found = True
            assert addon["is_installed"] is True
    assert found is True
    response, status = await cms_requester("POST", "/db/guillotina/@addons/email_validation/install")
    assert status == 412
