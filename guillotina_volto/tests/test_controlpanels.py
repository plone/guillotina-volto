import json

import pytest


pytestmark = pytest.mark.asyncio


async def test_controlpanels_languages(cms_requester):
    requester = cms_requester
    resp, status = await requester("GET", "/db/guillotina/@controlpanels")
    assert status == 200
    config = {
        "site_url": "http://localhost:4200",
        "validation_template": "validate.html",
        "validation_url": "/@@AnotherValidationEndpoint",
        "site_mails_from": "noreply@test.org",
    }
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/@controlpanels/validation_settings",
        data=json.dumps(config),
    )
    assert status == 204
    resp, status = await requester(
        "GET", "/db/guillotina/@controlpanels/validation_settings"
    )
    assert status == 200
    assert resp["data"]["validation_url"] == "/@@AnotherValidationEndpoint"
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/@controlpanels/language",
        data=json.dumps(
            {"available_languages": ["en", "es", "ca"], "default_language": "ca"}
        ),
    )
    assert status == 204
    resp, status = await requester("GET", "/db/guillotina/@controlpanels/language")
    assert status == 200
    assert resp["data"]["available_languages"] == ["en", "es", "ca"]
    resp, status = await requester("GET", "/db/guillotina/ca")
    assert status == 200
    resp, status = await requester("GET", "/db/guillotina/es")
    assert status == 200
    resp, status = await requester("GET", "/db/guillotina/en")
    assert status == 200
    resp, status = await requester("GET", "/db/guillotina/en/@translations")
    assert status == 200
    assert len(resp["items"]) == 2
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/@controlpanels/language",
        data=json.dumps(
            {"available_languages": ["en", "es", "ca", "de"], "default_language": "ca"}
        ),
    )
    assert status == 204
    resp, status = await requester("GET", "/db/guillotina/en/@translations")
    assert status == 200
    assert len(resp["items"]) == 3
    resp, status = await requester("GET", "/db/guillotina/de")
    assert status == 200
    resp, status = await requester(
        "POST",
        "/db/guillotina/es",
        data=json.dumps(
            {"@type": "Page", "id": "foo_page_es", "title": "Pàgina en espanol"}
        ),
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

    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca/@navroot",
    )
    assert status == 200
    assert resp["navroot"]["@name"] == "ca"

    resp, status = await requester(
        "GET",
        "/db/guillotina/es/foo_page_es/@translations",
    )
    assert status == 200
    assert len(resp["items"]) == 1
    assert resp["items"][0]["@id"] == "http://localhost/db/guillotina/ca/foo_page_ca"

    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca/@translations",
    )
    assert status == 200
    assert len(resp["items"]) == 1
    assert resp["items"][0]["@id"] == "http://localhost/db/guillotina/es/foo_page_es"

    resp, status = await requester(
        "POST",
        "/db/guillotina/en",
        data=json.dumps(
            {
                "@type": "Page",
                "id": "foo_page_en",
                "title": "Page in english",
                "translation_of": "/es/foo_page_es",
                "language": "en",
            }
        ),
    )
    assert status == 201

    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca/@translations",
    )
    assert status == 200
    assert len(resp["items"]) == 2

    resp, status = await requester(
        "POST",
        "/db/guillotina/de",
        data=json.dumps(
            {
                "@type": "Page",
                "id": "foo_page_de",
                "title": "Deutschland Page",
                "translation_of": "/en/foo_page_en",
                "language": "de",
            }
        ),
    )
    assert status == 201
    resp, status = await requester(
        "GET",
        "/db/guillotina/es/foo_page_es/@translations",
    )
    assert status == 200
    ca_found = False
    de_found = False
    en_found = False
    for item in resp["items"]:
        if item["@id"] == "http://localhost/db/guillotina/ca/foo_page_ca":
            ca_found = True
        elif item["@id"] == "http://localhost/db/guillotina/en/foo_page_en":
            en_found = True
        elif item["@id"] == "http://localhost/db/guillotina/de/foo_page_de":
            de_found = True
    assert ca_found is True
    assert en_found is True
    assert de_found is True
    resp, status = await requester("DELETE", "/db/guillotina/de/foo_page_de")
    assert status == 200
    resp, status = await requester(
        "GET",
        "/db/guillotina/es/foo_page_es/@translations",
    )
    assert status == 200
    assert len(resp["items"]) == 2
    ca_found = False
    de_found = False
    en_found = False
    for item in resp["items"]:
        if item["@id"] == "http://localhost/db/guillotina/ca/foo_page_ca":
            ca_found = True
        elif item["@id"] == "http://localhost/db/guillotina/en/foo_page_en":
            en_found = True
        elif item["@id"] == "http://localhost/db/guillotina/de/foo_page_de":
            de_found = True
    assert ca_found is True
    assert de_found is False
    assert en_found is True
    resp, status = await requester("DELETE", "/db/guillotina/es")
    assert status == 200
    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca/@translations",
    )
    assert status == 200
    assert len(resp["items"]) == 1
    assert resp["items"][0] == {
        "@id": "http://localhost/db/guillotina/en/foo_page_en",
        "language": "en",
    }
    assert "es" not in resp["root"]
    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/@search?id=foo_page_ca",
    )
    assert status == 200
    assert resp["items"][0]["paths_indexed"] == ["/en/foo_page_en"]
    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca?expand=translations,navroot",
    )
    assert status == 200
    assert (
        resp["@components"]["navroot"]["@id"]
        == "http://localhost/db/guillotina/ca/foo_page_ca/@navroot"
    )
    assert (
        resp["@components"]["navroot"]["navroot"]["@id"]
        == "http://localhost/db/guillotina/ca"
    )
    assert resp["@components"]["translations"]["items"][0] == {
        "@id": "http://localhost/db/guillotina/en/foo_page_en",
        "language": "en",
    }
    assert resp["language"] == {"title": "CA", "token": "ca"}
    resp, status = await requester(
        "GET",
        "/db/guillotina/ca/foo_page_ca/@translation-locator?target_language=en",
    )
    assert status == 200
    assert resp == {"@id": "http://localhost/db/guillotina/en"}
