import json
from guillotina import app_settings
from guillotina.utils import resolve_dotted_name
from guillotina.utils import get_registry

import pytest


pytestmark = pytest.mark.asyncio


async def test_controlpanels(cms_requester):
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
        "PATCH", "/db/guillotina/@controlpanels/validation_settings", data=json.dumps(config)
    )
    assert status == 204
    resp, status = await requester("GET", "/db/guillotina/@controlpanels/validation_settings")
    assert status == 200
    assert resp["data"]["validation_url"] == "/@@AnotherValidationEndpoint"
    resp, status = await requester(
        "PATCH", "/db/guillotina/@controlpanels/language", data=json.dumps({
            "available_languages": ["en", "es", "ca"],
            "default_language": "ca"
        })
    )
    assert status == 204
    resp, status = await requester("GET", "/db/guillotina/@controlpanels/language")
    assert status == 200
    assert resp["data"]["available_languages"] == ['en', 'es', 'ca']
    resp, status = await requester("GET", "/db/guillotina/ca")
    assert status == 200
    resp, status = await requester("GET", "/db/guillotina/es")
    assert status == 200
    resp, status = await requester("GET", "/db/guillotina/en")
    assert status == 200
    resp, status = await requester(
        "PATCH", "/db/guillotina/@controlpanels/language", data=json.dumps({
            "available_languages": ["en", "es", "ca", "de"],
            "default_language": "ca"
        })
    )
    assert status == 204
    resp, status = await requester("GET", "/db/guillotina/de")
    assert status == 200
