import pytest
import json
import asyncio
from guillotina.tests.test_catalog import PG_CATALOG_SETTINGS, NOT_POSTGRES

pytestmark = pytest.mark.asyncio


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_users(cms_requester):
    requester = cms_requester
    # create a payload of a user as I did in the user.py
    payload_user = {
        "email": "foo_user@guillotina.cat",
        "username": "foo_user",
        "name": "Foo",
        "password": "Foo12345",
    }
    resp, status = await requester(
        "POST", "/db/guillotina/@users", data=json.dumps(payload_user)
    )
    assert status == 200
    resp, status = await requester(
        "POST", "/db/guillotina/@users", data=json.dumps(payload_user)
    )
    assert status != 200
    resp, status = await requester("GET", "/db/guillotina/users/foo_user")
    assert status == 200
    resp, status = await requester(
        "POST",
        "/db/guillotina/@login",
        data=json.dumps({"login": "foo_user", "password": "Foo12345"}),
    )
    assert status == 200
    resp, status = await requester("GET", "/db/guillotina/@search?user_email=null")
    assert status == 200
    __import__("pdb").set_trace()
    resp, status = await requester("GET", "/db/guillotina/@users?search=foo")
    assert status == 200
    assert resp[0]["id"] == "foo_user"
    resp, status = await requester("GET", "/db/guillotina/@users")
    assert status == 200
    resp, status = await requester("GET", "/db/guillotina/@users?search=wrong")
    assert status == 200
