import json

import pytest
from guillotina.tests.test_catalog import NOT_POSTGRES
from guillotina.tests.test_catalog import PG_CATALOG_SETTINGS


pytestmark = pytest.mark.asyncio


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_create_page_with_image_preview_link(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "POST",
        "/db/guillotina",
        data=json.dumps({
            "@type": "Page",
            "id": "first_page",
            "title": "Primra pagina",
            "preview_caption_link": "Preview caption link text",
            "preview_image_link": {"@type":"Image", "id":"preview_image"},

        }),
    )
    assert status == 201

    resp, status = await requester(
        "GET",
        "/db/guillotina/first_page",
    )
    assert status == 200
    assert resp["preview_caption_link"] == "Preview caption link text"
    assert resp["preview_image_link"] == {"@type":"Image", "id":"preview_image"}

    resp, status = await requester(
        "PATCH",
        "/db/guillotina/first_page",
        data=json.dumps({
            "guillotina_volto.interfaces.base.ICMSBehavior": {
                "content_layout":"listing_view"
            },
        }),
    )
    assert status == 204

    resp, status = await requester(
        "GET",
        "/db/guillotina/first_page",
    )
    assert status == 200
    assert resp["preview_caption_link"] == "Preview caption link text"
    assert resp["preview_image_link"] == {"@type":"Image", "id":"preview_image"}




