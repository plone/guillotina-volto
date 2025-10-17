import json

import pytest
from guillotina.tests.test_catalog import NOT_POSTGRES
from guillotina.tests.test_catalog import PG_CATALOG_SETTINGS


pytestmark = pytest.mark.asyncio


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
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


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
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


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_multilanguage_navigation(cms_requester):
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

    resp, status = await requester("GET", "/db/guillotina/ca/?expand=navigation&expand.navigation.depth=1")
    assert status == 200
    assert len(resp["@components"]["navigation"]["items"]) == 1

    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca?expand=navigation&expand.navigation.depth=1",
    )
    assert status == 200
    assert len(resp["@components"]["navigation"]["items"]) == 1


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_multilanguage_locator(cms_requester):
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

    resp, status = await requester(
        "POST",
        "/db/guillotina/ca/foo_page_ca",
        data=json.dumps(
            {
                "@type": "Page",
                "id": "foo_page_ca_2",
                "title": "Una altra Pàgina en català",
            }
        ),
    )
    assert status == 201

    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca/@translation-locator?target_language=en",
    )
    assert status == 200
    assert resp == {"@id": "http://localhost/db/guillotina/en"}

    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca/foo_page_ca_2/@translation-locator?target_language=en",
    )
    assert status == 200
    assert resp == {"@id": "http://localhost/db/guillotina/en"}
    resp, status = await requester(
        "POST",
        "/db/guillotina/en",
        data=json.dumps(
            {
                "@type": "Page",
                "id": "foo_page_en",
                "title": "English Page",
                "translation_of": "/ca/foo_page_ca",
                "language": "en",
            }
        ),
    )
    assert status == 201
    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca/foo_page_ca_2/@translation-locator?target_language=en",
    )
    assert status == 200
    assert resp == {"@id": "http://localhost/db/guillotina/en/foo_page_en"}
