import json

import pytest


pytestmark = pytest.mark.asyncio


async def test_history_creation(cms_requester):
    requester = cms_requester
    resp, status = await requester(
        "POST",
        "/db/guillotina/",
        data=json.dumps({"@type": "Document", "title": "Document 1", "id": "doc1"}),
    )

    resp, status = await requester("GET", "/db/guillotina/doc1")
    assert status == 200
    assert (
        resp["guillotina.contrib.workflows.interfaces.IWorkflowBehavior"]["history"]
        is not None
    )
    assert (
        resp["guillotina_volto.interfaces.base.ICMSBehavior"]["history"]["0"]["actor"]
        == "root"
    )
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
    assert (
        resp["guillotina_volto.interfaces.base.ICMSBehavior"]["history"]["1"]["actor"]
        == "root"
    )
    assert resp["guillotina_volto.interfaces.base.ICMSBehavior"]["history"]["1"][
        "data"
    ] == {"title": "Document 2"}

    resp, status = await requester("GET", "/db/guillotina/doc1/@history")
    assert status == 200
    assert len(resp) == 2
    assert resp[0]["type"] == "Document"
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
                "guillotina.behaviors.dublincore.IDublinCore": {
                    "description": "Foo description 3"
                },
            }
        ),
    )
    assert status == 204
    resp, status = await requester(
        "GET",
        "/db/guillotina/doc1",
    )
    assert status == 200
    assert (
        resp["guillotina.behaviors.dublincore.IDublinCore"]["description"]
        == "Foo description 3"
    )

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
