import json

import pytest


pytestmark = pytest.mark.asyncio


async def test_unlink_translations(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/@controlpanels/language",
        data=json.dumps({"available_languages": ["en", "es", "ca"], "default_language": "ca"}),
    )
    assert status == 204

    resp, status = await requester(
        "POST",
        "/db/guillotina/es",
        data=json.dumps({"@type": "Page", "id": "foo_page_es", "title": "Pàgina en espanol"}),
    )
    assert status == 201

    resp, status = await requester(
        "POST",
        "/db/guillotina/ca",
        data=json.dumps(
            {
                "@type": "Page",
                "id": "foo_page_ca",
                "title": "Pàgina en català",
                "translation_of": "/es/foo_page_es",
                "language": "ca",
            }
        ),
    )
    assert status == 201

    resp, status = await requester("GET", "/db/guillotina/es/foo_page_es/?expand=translations,navroot")
    assert status == 200
    assert len(resp["@components"]["translations"]["items"]) == 1

    resp, status = await requester(
        "DELETE",
        "/db/guillotina/es/foo_page_es/@translations",
        data=json.dumps({"language": "ca"}),
    )
    assert status == 200

    resp, status = await requester("GET", "/db/guillotina/es/foo_page_es/@translations")
    assert status == 200
    assert len(resp["items"]) == 0

    resp, status = await requester(
        "DELETE",
        "/db/guillotina/es/foo_page_es/@translations",
        data=json.dumps({"language": "ca"}),
    )
    assert status == 200


async def test_link_translations(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/@controlpanels/language",
        data=json.dumps({"available_languages": ["en", "es", "ca"], "default_language": "ca"}),
    )
    assert status == 204

    resp, status = await requester(
        "POST",
        "/db/guillotina/es",
        data=json.dumps({"@type": "Page", "id": "foo_page_es", "title": "Pàgina en espanol"}),
    )
    assert status == 201

    resp, status = await requester(
        "POST",
        "/db/guillotina/ca",
        data=json.dumps({"@type": "Page", "id": "foo_page_ca", "title": "Pàgina en catala"}),
    )
    assert status == 201

    resp, status = await requester(
        "POST",
        "/db/guillotina/en",
        data=json.dumps({"@type": "Page", "id": "foo_page_en", "title": "Page in english"}),
    )
    assert status == 201

    resp, status = await requester(
        "POST",
        "/db/guillotina/en/foo_page_en/@translations",
        data=json.dumps({"id": "/ca/foo_page_ca"}),
    )
    assert status == 200

    resp, status = await requester("GET", "/db/guillotina/en/foo_page_en/@translations")
    assert status == 200
    assert len(resp["items"]) == 1

    resp, status = await requester("GET", "/db/guillotina/ca/foo_page_ca/@translations")
    assert status == 200
    assert len(resp["items"]) == 1

    resp, status = await requester(
        "POST",
        "/db/guillotina/en/foo_page_en/@translations",
        data=json.dumps({"id": "/ca/foo_page_ca"}),
    )
    assert status == 400
