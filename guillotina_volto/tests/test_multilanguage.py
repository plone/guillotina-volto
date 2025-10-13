import json

import pytest


pytestmark = pytest.mark.asyncio


async def test_multilanguage_get_language(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/@controlpanels/language",
        data=json.dumps({"available_languages": ["en", "es", "ca"], "default_language": "ca"}),
    )
    assert status == 204

    resp, status = await requester(
        "POST",
        "/db/guillotina/ca",
        data=json.dumps({"@type": "Page", "id": "foo_page_ca", "title": "Pàgina en català"}),
    )
    assert status == 201
    resp, status = await requester("GET", "/db/guillotina/ca")
    assert status == 200
    assert resp["language"] == {"title": "CA", "token": "ca"}
    resp, status = await requester("GET", "/db/guillotina/ca/foo_page_ca")
    assert status == 200
    assert resp["language"] == {"title": "CA", "token": "ca"}


async def test_not_multilanguage_no_language(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "POST",
        "/db/guillotina",
        data=json.dumps({"@type": "Page", "id": "foo_page_ca", "title": "Pàgina en català"}),
    )
    assert status == 201
    resp, status = await requester("GET", "/db/guillotina/foo_page_ca")
    assert status == 200
    assert "language" not in resp
