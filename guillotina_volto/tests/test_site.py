import json

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
    _, status = await cms_requester("GET", "/db/guillotina/@database")
    assert status == 200


async def test_validate_install_site(cms_requester):
    response, status = await cms_requester("GET", "/db/guillotina")
    assert status == 200

    response, status = await cms_requester("GET", "/db/guillotina/users")
    assert status == 200
    assert response["items"][0]["@id"] == "http://localhost/db/guillotina/users/admin"

    # login user admin
    response, status = await cms_requester(
        "POST", "/db/guillotina/@login", data=json.dumps({"login": "admin", "password": "admin"})
    )
    assert status == 200
    assert response["token"] is not None
    admin_token = response["token"]

    # get container
    response, status = await cms_requester("GET", "/db/guillotina", headers={"Authorization": f"Bearer {admin_token}"})
    assert status == 200

    # get users
    response, status = await cms_requester(
        "GET", "/db/guillotina/@users/admin", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert status == 200


async def test_get_querystring(cms_requester):
    response, status = await cms_requester("GET", "/db/guillotina/@querystring")
    assert status == 200
    assert len(response["indexes"]) == 7
    assert len(response["sortable_indexes"]) == 5
    assert "values" in response["indexes"]["type_name"]
    assert "values" in response["indexes"]["review_state"]
    assert "values" not in response["indexes"]["id"]
