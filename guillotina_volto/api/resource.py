from guillotina import configure
from guillotina.api.content import DefaultGET
from guillotina.interfaces import IResource
from guillotina.utils import get_current_request
from guillotina.utils import get_object_url

from guillotina_volto.api.components import Actions
from guillotina_volto.api.components import Breadcrumbs
from guillotina_volto.api.components import Navigation
from guillotina_volto.api.types import Types
from guillotina_volto.contrib.language.api import GetTranslations


@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.AccessContent",
    summary="Includes all the necessary information by volto",
    responses={
        "200": {
            "description": "Serialization",
            "schema": {"properties": {}},
        }
    },
)
class DefaultGETResource(DefaultGET):
    async def __call__(self):
        mapping_expansions = {
            "actions": {"class": Actions, "root": False, "component": True},
            "breadcrumbs": {"class": Breadcrumbs, "root": False, "component": True},
            "navigation": {"class": Navigation, "root": False, "component": True},
            "types": {"class": Types, "root": False, "component": True},
            "translations": {"class": GetTranslations, "root": False, "component": True},
        }
        full_response = await super().__call__()
        full_url = get_object_url(self.context)
        request = get_current_request()
        expansions = request.query.get("expand", [])
        if expansions:
            expansions = expansions.split(",")
        components = {
            "actions": {"@id": f"{full_url}/@actions"},
            "aliases": {"@id": f"{full_url}/@aliases"},
            "breadcrumbs": {"@id": f"{full_url}/@breadcrumbs"},
            "contextnavigation": {"@id": f"{full_url}/@contextnavigation"},
            "navigation": {"@id": f"{full_url}/@navigation"},
            "navroot": {"@id": f"{full_url}/@navroot"},
            "types": {"@id": f"{full_url}/@types"},
            "workflow": {"@id": f"{full_url}/@workflow"},
            "translations": {"@id": f"{full_url}/@translations"},
        }
        for expand in expansions:
            mapping_payload = mapping_expansions.get(expand, None)
            if mapping_payload is None:
                continue
            mapping_class = mapping_payload.get("class", None)
            if mapping_class:
                response = await mapping_class.__call__(self)
                if "@id" in response:
                    response["@id"] = f"{full_url}/@{expand}"
                if mapping_payload.get("component") is True:
                    components[expand] = response
                elif mapping_payload.get("root") is True:
                    full_response[expand] = response
        full_response["@components"] = components
        return full_response
