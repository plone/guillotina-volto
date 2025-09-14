import json
import os

import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.skipif(
    os.environ.get("DATABASE", "DUMMY") in ("cockroachdb", "DUMMY"),
    reason="Not for dummy db",
)
async def test_navigation(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "POST",
        "/db/guillotina/",
        data=json.dumps({"@type": "CMSFolder", "id": "folder1"}),
    )
    assert status == 201
    resp, status = await requester(
        "POST",
        "/db/guillotina/folder1",
        data=json.dumps({"@type": "Document", "id": "doc1"}),
    )
    assert status == 201
    resp, status = await requester(
        "POST",
        "/db/guillotina/folder1",
        data=json.dumps({"@type": "Document", "id": "doc2"}),
    )
    assert status == 201
    resp, status = await requester("GET", "/db/guillotina/@navigation?expand.navigation.depth=2")
    assert len(resp["items"][0]["items"]) == 2
