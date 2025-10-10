import json

import pytest
from guillotina.tests.test_catalog import NOT_POSTGRES
from guillotina.tests.test_catalog import PG_CATALOG_SETTINGS


pytestmark = pytest.mark.asyncio


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
@pytest.mark.skip(
    reason="Not implemented in guillotina 7.0.5, implemented in next version"
)
async def test_permissions_site_managers_group(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "POST",
        "/db/guillotina/@login",
        data=json.dumps({"login": "admin", "password": "admin"}),
    )
    assert status == 200
    admin_token = resp["token"]

    resp, status = await requester(
        "GET",
        "/db/guillotina/@items",
        authenticated=False,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert status == 200

    resp, status = await requester(
        "POST",
        "/db/guillotina/",
        data=json.dumps({"@type": "Document", "title": "Document 1", "id": "doc2"}),
        authenticated=False,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert status == 201

    resp, status = await requester(
        "PATCH",
        "/db/guillotina/",
        data=json.dumps({"title": "Container edited by admin"}),
        authenticated=False,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert status == 204

    payload_user = {
        "email": "foo_user@guillotina.cat",
        "username": "foo_user",
        "name": "Foo",
        "password": "Foo12345",
        "user_groups": ["managers"],
    }
    resp, status = await requester(
        "POST", "/db/guillotina/@users", data=json.dumps(payload_user)
    )
    assert status == 200

    resp, status = await requester(
        "POST",
        "/db/guillotina/@login",
        data=json.dumps({"login": "foo_user", "password": "Foo12345"}),
    )
    assert status == 200
    token = resp["token"]

    resp, status = await requester(
        "POST",
        "/db/guillotina/",
        data=json.dumps({"@type": "Document", "title": "Document 3", "id": "doc3"}),
        authenticated=False,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert status == 201

    resp, status = await requester(
        "PATCH",
        "/db/guillotina/",
        data=json.dumps({"title": "Container edited by second user"}),
        authenticated=False,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert status == 204

    # Create a new site to validat that a manager from other container can not access it
    resp, status = await requester(
        "POST",
        "/db",
        data=json.dumps(
            {
                "@type": "Site",
                "title": "Title guillotina volto",
                "id": "guillotina_volto",
            }
        ),
    )
    assert status == 200

    resp, status = await requester(
        "GET",
        "/db/guillotina_volto/",
        authenticated=False,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert status == 401

    resp, status = await requester(
        "POST",
        "/db/guillotina_volto/",
        data=json.dumps({"@type": "Document", "title": "Document 3", "id": "doc3"}),
        authenticated=False,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert status == 401


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
@pytest.mark.skip(
    reason="Not implemented in guillotina 7.0.5, implemented in next version"
)
async def test_permissions_create_site_admins_group(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "POST",
        "/db/guillotina/@groups",
        data=json.dumps(
            {
                "@type": "Group",
                "title": "Site Admins",
                "groupname": "site_admins",
                "id": "site_admins",
                "description": "Site Admins Group",
                "roles": [
                    "guillotina.Manager",
                    "guillotina.ContainerAdmin",
                    "guillotina.Owner",
                ],
            }
        ),
    )
    assert status == 200

    payload_user = {
        "email": "foo_user@guillotina.cat",
        "username": "foo_user",
        "name": "Foo",
        "password": "Foo12345",
        "user_groups": ["site_admins"],
    }
    resp, status = await requester(
        "POST", "/db/guillotina/@users", data=json.dumps(payload_user)
    )
    assert status == 200

    resp, status = await requester(
        "POST",
        "/db/guillotina/@login",
        data=json.dumps({"login": "foo_user", "password": "Foo12345"}),
    )
    assert status == 200
    token = resp["token"]

    resp, status = await requester(
        "POST",
        "/db/guillotina/",
        data=json.dumps({"@type": "Document", "title": "Document 1", "id": "doc2"}),
        authenticated=False,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert status == 201

    resp, status = await requester(
        "PATCH",
        "/db/guillotina/",
        data=json.dumps({"title": "Container edited by admin"}),
        authenticated=False,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert status == 204
