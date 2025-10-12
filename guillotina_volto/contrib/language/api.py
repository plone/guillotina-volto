from guillotina import configure
from guillotina.api.service import Service
from guillotina.content import create_content_in_container
from guillotina.contrib.dbusers.services.users import ListUsers
from guillotina.event import notify
from guillotina.events import ObjectAddedEvent
from guillotina_volto.utils import Search
from guillotina.interfaces import IResource
from guillotina_volto.contrib.language.behaviors import ILanguageBehavior
from guillotina.utils import get_behavior


@configure.service(
    context=IResource,
    name="@translations",
    permission="guillotina.AccessContent",
    summary="Get available translations",
    method="GET",
    responses={
        "200": {
            "description": "Get all the translations related to the object",
        }
    },
)
class GetTranslations(Service):
    async def __call__(self):
        results = {"items": [], "root": {}, "@id": self.request.url}
        bhr_obj_translated = await get_behavior(self.context, ILanguageBehavior)
        for translation in bhr_obj_translated.translations.values():
            payload = {
                "@id": translation["@id"],
                "language": translation["language"]
            }
            results["items"].append(payload)
        search_instance = Search()
        results_folders = await search_instance.search_raw(unrestricted=False, query={"type_name": "LanguageFolder"})
        for result in results_folders["items"]:
            results["root"][result["@name"]] = result["@id"]
        return results
