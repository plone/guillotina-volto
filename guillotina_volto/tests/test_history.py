import json

import pytest
from guillotina.tests.test_catalog import NOT_POSTGRES
from guillotina.tests.test_catalog import PG_CATALOG_SETTINGS


pytestmark = pytest.mark.asyncio

payload_document_with_blocks = {
    "title": "Title",
    "parent": {"@id": "http://127.0.0.1:8081/db/container"},
    "@static_behaviors": [
        "guillotina_volto.interfaces.base.ICMSBehavior",
        "guillotina_volto.interfaces.blocks.IBlocks",
    ],
    "@type": "Document",
    "guillotina_volto.interfaces.base.ICMSBehavior": {"content_layout": "default", "position_in_parent": -1},
    "guillotina_volto.interfaces.blocks.IBlocks": {
        "blocks_layout": {"items": ["29944f41-3c9b-4ce3-bcdf-f1074df81c33", "a4cc9e96-3559-4cbb-8e7d-c332703cf372"]},
        "blocks": {
            "29944f41-3c9b-4ce3-bcdf-f1074df81c33": {"@type": "title"},
            "a4cc9e96-3559-4cbb-8e7d-c332703cf372": {
                "@type": "slate",
                "value": [{"type": "p", "children": [{"text": "Text"}]}],
                "plaintext": "Text",
            },
        },
    },
    "id": "doc1",
}


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_history_creation(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "POST",
        "/db/guillotina/",
        data=json.dumps({"@type": "Document", "title": "Document 1", "id": "doc1"}),
    )

    resp, status = await requester("GET", "/db/guillotina/doc1")
    assert status == 200
    assert resp["guillotina.contrib.workflows.interfaces.IWorkflowBehavior"]["history"] is not None
    assert resp["guillotina_volto.interfaces.base.ICMSBehavior"]["history"]["0"]["actor"] == "root"
    assert isinstance(
        resp["guillotina_volto.interfaces.base.ICMSBehavior"]["history"]["0"]["data"],
        dict,
    )
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/doc1",
        data=json.dumps({"title": "Document 2"}),
    )
    assert status == 204
    resp, status = await requester("GET", "/db/guillotina/doc1")
    assert status == 200
    assert resp["guillotina_volto.interfaces.base.ICMSBehavior"]["history"]["1"]["actor"] == "root"
    assert resp["guillotina_volto.interfaces.base.ICMSBehavior"]["history"]["1"]["data"] == {"title": "Document 2"}

    resp, status = await requester("GET", "/db/guillotina/doc1/@history")
    assert status == 200
    assert len(resp) == 2
    assert resp[0]["type"] == "versioning"
    assert resp[0]["transition_title"] == "Object created"
    assert resp[1]["transition_title"] == "Object modified"
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/doc1",
        data=json.dumps({"title": "Document 3", "description": "Foo description 1"}),
    )
    assert status == 204
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/doc1",
        data=json.dumps({"title": "Document 4", "description": "Foo description 2"}),
    )
    assert status == 204
    resp, status = await requester(
        "PATCH",
        "/db/guillotina/doc1",
        data=json.dumps(
            {
                "guillotina.behaviors.dublincore.IDublinCore": {"description": "Foo description 3"},
            }
        ),
    )
    assert status == 204
    resp, status = await requester(
        "GET",
        "/db/guillotina/doc1",
    )
    assert status == 200
    assert resp["guillotina.behaviors.dublincore.IDublinCore"]["description"] == "Foo description 3"

    resp, status = await requester(
        "GET",
        "/db/guillotina/doc1/@history",
    )
    assert status == 200
    assert len(resp) == 5

    resp, status = await requester(
        "PATCH",
        "/db/guillotina/doc1/@history",
        data=json.dumps({"version": "0"}),
    )
    assert status == 200
    resp, status = await requester(
        "GET",
        "/db/guillotina/doc1",
    )
    assert status == 200
    assert resp["guillotina.behaviors.dublincore.IDublinCore"]["description"] is None
    assert resp["title"] == "Document 1"
    resp, status = await requester(
        "GET",
        "/db/guillotina/doc1/@history",
    )
    assert status == 200
    assert len(resp) == 6

    resp, status = await requester(
        "PATCH",
        "/db/guillotina/doc1/@history",
        data=json.dumps({"version": "1"}),
    )
    assert status == 200
    resp, status = await requester(
        "GET",
        "/db/guillotina/doc1",
    )
    assert status == 200
    assert resp["title"] == "Document 2"

    resp, status = await requester("GET", "/db/guillotina/doc1/@history/2")
    assert status == 200
    assert resp["title"] == "Document 3"

    resp, status = await requester("POST", "/db/guillotina/doc1/@workflow/publish", data=json.dumps({}))
    assert status == 200

    resp, status = await requester(
        "GET",
        "/db/guillotina/doc1/@history",
    )
    assert status == 200
    assert resp[7]["type"] == "workflow"
    assert resp[7]["action"] == "publish"
    assert resp[7]["state_title"] == "Public"
    assert resp[7]["review_state"] == "public"
    assert len(resp) == 8

    resp, status = await requester(
        "GET",
        "/db/guillotina/doc1/@history/2?expand=breadcrumbs,actions,types,navroot,navigation,inherit",
    )
    assert status == 200
    assert resp["title"] == "Document 3"


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_history_merge(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "POST",
        "/db/guillotina/",
        data=json.dumps(payload_document_with_blocks),
    )
    assert status == 201

    resp, status = await requester(
        "PATCH",
        "/db/guillotina/doc1",
        data=json.dumps(
            {
                "guillotina_volto.interfaces.blocks.IBlocks": {
                    "blocks_layout": {
                        "items": [
                            "29944f41-3c9b-4ce3-bcdf-f1074df81c33",
                            "a4cc9e96-3559-4cbb-8e7d-c332703cf372",
                            "b4cc9e96-3559-4cbb-8e7d-c332703cf373",
                        ]
                    }
                }
            }
        ),
    )
    assert status == 204

    resp, status = await requester("GET", "/db/guillotina/doc1/@history/1")
    assert status == 200
    assert "blocks_layout" in resp["guillotina_volto.interfaces.blocks.IBlocks"]
    assert "blocks" in resp["guillotina_volto.interfaces.blocks.IBlocks"]
