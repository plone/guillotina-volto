from zope.interface import Interface
from datetime import datetime
from dateutil.tz import tzutc
from guillotina import configure
from guillotina import schema
from guillotina.behaviors.instance import AnnotationBehavior
from guillotina.behaviors.properties import ContextProperty
from guillotina.directives import index_field
from guillotina.fields.patch import PatchField
from zope.interface import Interface

TRANSLATIONS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Localized Page",
    "type": "object",
    "required": ["@id", "language"],
    "properties": {
        "@id": {
            "type": "string",
            "format": "uri",
            "description": "The URL of the localized page"
        },
        "language": {
            "type": "string",
            "pattern": "^[a-z]{2}(-[A-Z]{2})?$",
            "description": "Language code (e.g. 'en', 'ca', 'it', 'en-US')"
        }
    },
    "additionalProperties": False
}

class IMarkerLanguagebehavior(Interface):
    """Marker interface for content with dublin core."""

class ILanguageBehavior(Interface):
    translations = schema.List(value_type=schema.JSONField(schema=TRANSLATIONS_SCHEMA))
    language = schema.TextLine()

@configure.behavior(
    title="Language behavior",
    provides=ILanguageBehavior,
    marker=IMarkerLanguagebehavior,
    for_="guillotina.interfaces.IResource",
)
class LanguageBehavior(AnnotationBehavior):
    language = ContextProperty("title", None)

    def __init__(self, context):
        self.__dict__["context"] = context
        super(LanguageBehavior, self).__init__(context)
