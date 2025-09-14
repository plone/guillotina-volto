import json

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
