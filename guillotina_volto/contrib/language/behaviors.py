from guillotina import configure
from guillotina import schema
from guillotina.behaviors.instance import ContextBehavior
from guillotina.directives import index_field
from guillotina.interfaces import IResource
from guillotina.utils import get_behavior
from zope.interface import Interface


TRANSLATIONS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Localized Page",
    "type": "object",
    "required": ["@id", "language", "path"],
    "properties": {
        "@id": {
            "type": "string",
            "format": "uri",
            "description": "The URL of the localized page",
        },
        "language": {
            "type": "string",
            "pattern": "^[a-z]{2}(-[A-Z]{2})?$",
            "description": "Language code (e.g. 'en', 'ca', 'it', 'en-US')",
        },
    },
    "additionalProperties": False,
}


class IMarkerLanguagebehavior(Interface):
    """Marker interface for content with dublin core."""


class ILanguageBehavior(Interface):
    translations = schema.Dict(
        key_type=schema.TextLine(title="Path of the related translation"),
        value_type=schema.JSONField(schema=TRANSLATIONS_SCHEMA),
        default={},
        defaultFactory=dict,
        missing_value={},
    )
    index_field("language", type="keyword")
    language = schema.TextLine()


@configure.behavior(
    title="Language behavior",
    provides=ILanguageBehavior,
    marker=IMarkerLanguagebehavior,
    for_="guillotina.interfaces.IResource",
)
class LanguageBehavior(ContextBehavior):
    pass


@index_field.with_accessor(
    IResource,
    "paths_indexed",
    field="translations",
    behavior="guillotina_volto.contrib.language.behaviors.ILanguageBehavior",
    type="text",
    store=True,
)
async def last_creation_date_review(obj):
    bhr = await get_behavior(obj, ILanguageBehavior)
    all_paths = []
    if bhr:
        for translation in bhr.translations.keys():
            all_paths.append(translation)
    return all_paths
