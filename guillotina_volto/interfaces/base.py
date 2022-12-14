import json

from guillotina import schema
from guillotina.directives import index_field
from zope.interface import Interface

from guillotina_volto.directives import fieldset


DISCUSSION_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {
            "@parent": {"type": "string"},
            "@type": {"type": "string"},
            "author_name": {"type": "string"},
            "author_username": {"type": "string"},
            "creation_date": {"type": "string"},
            "in_reply_to": {"type": "string"},
            "is_deletable": {"type": "boolean"},
            "is_editable": {"type": "boolean"},
            "modification_date": {"type": "boolean"},
            "text": {
                "type": "object",
                "properties": {
                    "data": {"type": "string"},
                    "mime-type": {"type": "string"},
                },
            },
            "user_notification": {"type": "boolean"},
        },
    }
)


HISTORY_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {
            "actor": {"type": "string"},
            "comments": {"type": "string"},
            "time": {"type": "string"},
            "type": {"type": "string"},
            "title": {"type": "string"},
            "data": {"type": "object", "properties": {}},
        },
    }
)


class ICMSLayer(Interface):
    """Marker interface layer Plone.CMS."""


class ICMSBehavior(Interface):

    index_field("is_folderish", store=True, type="boolean")
    is_folderish = schema.Bool(title="Is a folderish object", readonly=True)

    index_field("hidden_navigation", store=True, type="boolean")
    fieldset("hidden_navigation", "settings")
    hidden_navigation = schema.Bool(
        title="Should be hidden on navigation", required=False, default=False
    )

    index_field("language", store=True, type="keyword")
    fieldset("language", "categorization")
    language = schema.Choice(title="Language", required=False, source="languages")

    index_field("content_layout", store=True, type="keyword")
    fieldset("content_layout", "settings")
    content_layout = schema.Choice(
        title="Content Layout",
        required=False,
        source="content_layouts",
        default="default",
    )

    fieldset("allow_discussion", "settings")
    allow_discussion = schema.Bool(
        title="Allow discussion", required=False, default=False
    )

    # not absolute positioning, just a relative positioning
    # based on ordered numbers. It won't be numbers like 1,2,3,4,5,etc
    index_field("position_in_parent", type="int")
    position_in_parent = schema.Int(
        title="Position in parent", default=-1, required=False
    )

    comments = schema.Dict(
        title="Comments list field",
        required=False,
        key_type=schema.TextLine(title="CommentID"),
        value_type=schema.JSONField(title="Comment", schema=DISCUSSION_SCHEMA),
    )
