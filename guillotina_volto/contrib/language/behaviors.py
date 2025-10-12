from zope.interface import Interface
from guillotina import configure
from guillotina import schema
from guillotina.behaviors.properties import ContextProperty
from guillotina.behaviors.instance import ContextBehavior

TRANSLATIONS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Localized Page",
    "type": "object",
    "required": ["@id", "language", "path"],
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
        },
        "path": {
            "type": "string"
        },
    },
    "additionalProperties": False
}

class IMarkerLanguagebehavior(Interface):
    """Marker interface for content with dublin core."""

class ILanguageBehavior(Interface):
    translations = schema.List(
        value_type=schema.JSONField(schema=TRANSLATIONS_SCHEMA),
        default=[],
        defaultFactory=list,
        missing_value=list
    )
    language = schema.TextLine()

@configure.behavior(
    title="Language behavior",
    provides=ILanguageBehavior,
    marker=IMarkerLanguagebehavior,
    for_="guillotina.interfaces.IResource",
)
class LanguageBehavior(ContextBehavior):
    language = ContextProperty("language", None)
