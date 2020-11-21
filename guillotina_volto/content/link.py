# -*- encoding: utf-8 -*-
from guillotina import configure
from guillotina.content import Item
from guillotina.interfaces import IItem
from guillotina import schema
from guillotina_volto import _
from guillotina.directives import index_field


class ILink(IItem):

    index_field("url", store=True, type="text")
    url = schema.TextLine(title=_("URL"), required=False)


@configure.contenttype(
    type_name="Link",
    schema=ILink,
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina.contrib.workflows.interfaces.IWorkflowBehavior",
        "guillotina_volto.interfaces.base.ICMSBehavior",
    ],
    allowed_types=[],  # dynamically calculated
)
class Link(Item):
    pass
