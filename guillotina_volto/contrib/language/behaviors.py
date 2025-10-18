from guillotina import configure
from guillotina import schema
from guillotina.behaviors.instance import ContextBehavior
from guillotina.directives import index_field
from guillotina.event import notify
from guillotina.events import ObjectModifiedEvent
from guillotina.interfaces import IResource
from guillotina.response import HTTPBadRequest
from guillotina.utils import get_behavior
from guillotina.utils import get_content_path
from guillotina.utils import get_current_container
from guillotina.utils import get_object_url
from guillotina.utils import navigate_to
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
    def __init__(self, context):
        self.__dict__["context"] = context
        super(LanguageBehavior, self).__init__(context)

    async def link_translation(self, translation_of):
        current_path = get_content_path(self.context)
        current_language = current_path.strip("/").split("/")[0]
        language = translation_of.strip("/").split("/")[0]

        container = get_current_container()
        full_url_container = get_object_url(container)
        payload = {
            "@id": f"{full_url_container}{translation_of}",
            "language": language,
        }
        self.language = current_language
        # Update all the other transalations. Go over every related
        # one and update them all
        if self.translations == {}:
            # I need to set this first before doing an append. WHY?
            self.translations = {}
        self.translations[translation_of] = payload
        await notify(ObjectModifiedEvent(self, payload={"translations": self.translations}))
        payload_current_object = {
            "@id": f"{full_url_container}{current_path}",
            "language": current_language,
        }
        obj_translated_of = await navigate_to(container, translation_of)
        bhr_obj_translated_from = await get_behavior(obj_translated_of, ILanguageBehavior)
        bhr_obj_translated_from.language = language
        if bhr_obj_translated_from.translations == {}:
            bhr_obj_translated_from.translations = {}
        for path, translation in bhr_obj_translated_from.translations.items():
            language = translation["language"]
            if language == current_language:
                raise HTTPBadRequest(
                    content={
                        "error": {
                            "message": "translation already added",
                            "type": "BadRequest",
                        }
                    }
                )
            try:
                obj_translated_of = await navigate_to(container, path)
            except KeyError:
                continue
            payload = {"@id": f"{full_url_container}{path}", "language": language}
            self.translations[path] = payload
            bhr_obj_translated = await get_behavior(obj_translated_of, ILanguageBehavior)
            if bhr_obj_translated.translations == {}:
                bhr_obj_translated.translations = {}
            bhr_obj_translated.translations[current_path] = payload_current_object
            bhr_obj_translated.register()
            obj_translated_of.register()
            await notify(
                ObjectModifiedEvent(
                    bhr_obj_translated,
                    payload={"translations": bhr_obj_translated.translations},
                )
            )
        bhr_obj_translated_from.translations[current_path] = payload_current_object
        await notify(
            ObjectModifiedEvent(
                bhr_obj_translated_from,
                payload={"translations": bhr_obj_translated_from.translations},
            )
        )
        bhr_obj_translated_from.register()
        self.register()
        self.register()


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
