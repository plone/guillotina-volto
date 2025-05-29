import json
import pytest

pytestmark = pytest.mark.asyncio


async def _test_history_creation(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "POST",
        "/db/guillotina/",
        data=json.dumps({
            "@type": "Document",
            "title": "Document 1",
            "id": "doc1"
        }),
    )

    resp, status = await requester("GET", "/db/guillotina/doc1")
    assert (
        resp["guillotina.contrib.workflows.interfaces.IWorkflowBehavior"]["history"] is not None
    )
    resp, status = await requester("GET", "/db/guillotina/doc1/@workflow")
    assert status == 200
    resp, status = await requester("GET", "/db/guillotina/doc1")

