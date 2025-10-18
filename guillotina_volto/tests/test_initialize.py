import pytest


pytestmark = pytest.mark.asyncio


async def test_initialize(cms_requester):
    requester = cms_requester
    resp, status = await requester("GET", "/db/guillotina/@types/Container")
    assert status == 200
    assert "guillotina_volto.interfaces.blocks.IBlocks" in resp["properties"]
    assert "guillotina_volto.interfaces.base.ICMSBehavior" in resp["properties"]
    assert "guillotina.behaviors.dublincore.IDublinCore" in resp["properties"]
