from guillotina import configure
from guillotina_volto.interfaces.content import ISite
from guillotina.interfaces import IAbsoluteURL
from guillotina.interfaces import ISchemaFieldSerializeToJson
from guillotina.component import getMultiAdapter
from guillotina.component import get_multi_adapter
from guillotina.contrib.email_validation.interfaces import IValidationSettings
from guillotina.schema import get_fields_in_order
from guillotina.utils import get_registry

from importlib.metadata import version
import platform


@configure.service(
    context=ISite, method='GET', permission='guillotina.AccessControlPanel',
    name='@controlpanels')
async def controlpanel(context, request):

    url = getMultiAdapter((context, request), IAbsoluteURL)()

    return [{
        "@id": f"{url}/@controlpanels/image_settings",
        "group": "General",
        "title": "Image Settings"
    },
    {
        "@id": f"{url}/@controlpanels/validation_settings",
        "group": "General",
        "title": "Validations Settings"
    }]

@configure.service(
    context=ISite, method='GET', permission='guillotina.AccessControlPanel',
    name="@controlpanels/{type_id}")
async def controlpanel_element(context, request):

    url = getMultiAdapter((context, request), IAbsoluteURL)()
    type_id = request.matchdict["type_id"]
    registry = await get_registry()

    result = {
        "@id": f"{url}/@controlpanels/{type_id}",
        "group": "General",
        "title": "Validations Settings",
        "data": {}
    }
    if type_id == 'validation_settings':
        config = registry.for_interface(IValidationSettings)
        schema = {
            "properties": {},
            "fieldsets": [],
            "required": []
        }
        data = {}
        fields = []
        for name, field in get_fields_in_order(IValidationSettings):
            if field.required:
                result["required"].append(name)
            serializer = get_multi_adapter((field, IValidationSettings, request), ISchemaFieldSerializeToJson)
            schema["properties"][name] = await serializer()
            data[name] = config.__getitem__(name)
            fields.append(name)
        schema['fieldsets'] = [{
            'fields': fields,
            'id': 'default',
            'title': 'default'
        }]
        result['schema'] = schema
        result['data'] = data

    return result


@configure.service(
    context=ISite, method='PATCH', permission='guillotina.AccessControlPanel',
    name="@controlpanels/{type_id}")
async def controlpanel_element(context, request):
    payload = await request.json()
    url = getMultiAdapter((context, request), IAbsoluteURL)()
    type_id = request.matchdict["type_id"]

    result = {
        "@id": f"{url}/@controlpanels/{type_id}",
        "group": "General",
        "title": "Validations Settings",
        "data": {}
    }
    registry = await get_registry()
    if type_id == 'validation_settings':
        config = registry.for_interface(IValidationSettings)
        for key, value in payload.items():
            if key in IValidationSettings:
                config.__setitem__(key, value)
    return result
