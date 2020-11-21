# -*- encoding: utf-8 -*-
from guillotina import configure
from guillotina.content import Item
from guillotina_volto.interfaces import IEvent


@configure.contenttype(
    type_name="Event",
    schema=IEvent,
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina.contrib.workflows.interfaces.IWorkflowBehavior",
        "guillotina_volto.interfaces.base.ICMSBehavior",
    ],
    allowed_types=["Image", "File"],  # dynamically calculated
)
class Event(Item):
    pass
