import pytest
import json

pytestmark = pytest.mark.asyncio


async def test_users(cms_requester):
    requester = cms_requester
    # create a payload of a user as I did in the user.py
    payload_user = {
        "email": "foo_user@guillotina.cat",
        "username": "foo_user",
        "name": "Foo",
        "password": "Foo12345"
    }
    resp, status = await requester("POST", "/db/guillotina/@users", data=json.dumps(payload_user))
    assert status == 200
    resp, status = await requester("POST", "/db/guillotina/@users", data=json.dumps(payload_user))
    assert status != 200
    resp, status = await requester("GET", "/db/guillotina/users/foo_user")
    assert status == 200
    resp, status = await requester(
        "POST",
        "/db/guillotina/@login",
        data=json.dumps({"login": "foo_user", "password": "Foo12345"})
    )
    assert status == 200
