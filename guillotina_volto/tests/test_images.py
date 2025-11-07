import base64
import json

import pytest
from guillotina.utils import resolve_path

from guillotina_volto.behaviors.image import IImageAttachment


pytestmark = pytest.mark.asyncio


async def _add_image(requester, path):
    image_path = resolve_path("guillotina:static/assets/apple-touch-icon-144x144.png")
    with open(image_path, "rb") as fi:
        image_data = base64.b64encode(fi.read()).decode("utf-8")
    await requester(
        "PATCH",
        path,
        data=json.dumps(
            {
                IImageAttachment.__identifier__: {
                    "image": {
                        "filename": "logo.png",
                        "content-type": "image/png",
                        "encoding": "base64",
                        "data": image_data,
                    }
                }
            }
        ),
    )


async def test_add_container_logo(cms_requester):
    requester = cms_requester
    await _add_image(requester, "/db/guillotina")

    resp, status = await requester("GET", "/db/guillotina/@download/image")
    assert status == 200
    assert len(resp) > 0

    resp, status = await requester("GET", "/db/guillotina/@@images/image")
    assert status == 200
    assert len(resp) > 0


async def test_get_scales(cms_requester):
    requester = cms_requester
    await _add_image(requester, "/db/guillotina")
    resp, status = await requester("GET", "/db/guillotina/@@images/image/mini")
    assert status == 200
    assert len(resp) > 0


async def test_fourohfour_when_no_image(cms_requester):
    requester = cms_requester
    resp, status = await requester("GET", "/db/guillotina/@@images/foobar")
    assert status == 404


async def test_fourohfour_when_invalid_scale(cms_requester):
    requester = cms_requester
    await _add_image(requester, "/db/guillotina")
    resp, status = await requester("GET", "/db/guillotina/@@images/image/foobar")
    assert status == 404


async def test_get_scales_on_image_content(cms_requester):
    requester = cms_requester
    image_path = resolve_path("guillotina:static/assets/apple-touch-icon-144x144.png")
    with open(image_path, "rb") as fi:
        image_data = base64.b64encode(fi.read()).decode("utf-8")
    _, status = await requester(
        "POST",
        "/db/guillotina",
        data=json.dumps(
            {
                "id": "logo.png",
                "@type": "Image",
                "image": {
                    "filename": "logo.png",
                    "content-type": "image/png",
                    "encoding": "base64",
                    "data": image_data,
                },
            }
        ),
    )
    assert status == 201

    resp, status = await requester("GET", "/db/guillotina/logo.png")
    assert status == 200

    resp, status = await requester("GET", "/db/guillotina/logo.png/@@images/image/mini")
    assert status == 200
    assert len(resp) > 0

async def test_serialize_scales_on_image_content(cms_requester):
    requester = cms_requester
    image_path = resolve_path("guillotina:static/assets/apple-touch-icon-144x144.png")
    with open(image_path, "rb") as fi:
        image_data = base64.b64encode(fi.read()).decode("utf-8")
    resp, status = await requester(
        "POST",
        "/db/guillotina",
        data=json.dumps({
            "@type": "Page",
            "id": "first_page",
            "title": "Primra pagina",
        }),
    )
    assert status == 201
    resp, status = await cms_requester(
        "POST",
        "/db/guillotina/first_page",
        data=json.dumps(
            {
                "id": "logo.png",
                "@type": "Image",
                "image": {
                    "filename": "logo.png",
                    "content-type": "image/png",
                    "encoding": "base64",
                    "data": image_data,
                },
            }
        ),
    )
    assert status == 201
    assert '/first_page/logo.png' in resp['image_scales']['image'][0]['download']
    assert 'scales' in resp['image_scales']['image'][0]

    resp, status = await cms_requester("GET", "/db/guillotina/first_page/@search?type_name=Image")
    assert status == 200
    assert resp['items'][0]['image_scales']['image'][0]['base_path'] == '/first_page/logo.png'
    assert '/first_page/logo.png' in resp['items'][0]['image_scales']['image'][0]['download']

    resp, status = await cms_requester("GET", "/db/guillotina/first_page/logo.png")
    assert status == 200
    assert '/first_page/logo.png' in resp['image']['download']
    assert 'scales' in resp['image']

    resp, status = await cms_requester("GET", "/db/guillotina/first_page")
    assert status == 200
    assert resp['items'][0]['image_scales']['image'][0]['base_path'] == '/first_page/logo.png'
    assert '/first_page/logo.png' in resp['items'][0]['image_scales']['image'][0]['download']
