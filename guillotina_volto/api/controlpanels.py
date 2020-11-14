from guillotina import configure
from guillotina_volto.interfaces.content import ISite
from guillotina.interfaces import IAbsoluteURL
from guillotina.interfaces import ISchemaFieldSerializeToJson
from guillotina.component import getMultiAdapter
from guillotina.component import get_multi_adapter
from guillotina.contrib.email_validation.interfaces import IValidationSettings
from guillotina.schema import get_fields_in_order
from guillotina.utils import resolve_dotted_name
from guillotina.utils import get_registry
from guillotina import app_settings


@configure.service(
    context=ISite, method='GET', permission='guillotina.AccessControlPanel',
    name='@controlpanels')
async def controlpanel(context, request):

    url = getMultiAdapter((context, request), IAbsoluteURL)()

    result = []
    for item, value in app_settings.get('controlpanels', {}):
        result.append({
            "@id": f"{url}/@controlpanels/{item}",
            "group": value['group'],
            "title": value['title']
        })
    return result

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

    controlpanels = app_settings.get('controlpanels', {})
    if type_id in controlpanels:
        schema = controlpanels[type_id].get('schema', None)
        if schema is None:
            return
        schemaObj = resolve_dotted_name(schema)
        config = registry.for_interface(schemaObj)
        schema = {
            "properties": {},
            "fieldsets": [],
            "required": []
        }
        data = {}
        fields = []
        for name, field in get_fields_in_order(schemaObj):
            if field.required:
                result["required"].append(name)
            serializer = get_multi_adapter((field, schemaObj, request), ISchemaFieldSerializeToJson)
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
    type_id = request.matchdict["type_id"]

    registry = await get_registry()
    controlpanels = app_settings.get('controlpanels', {})
    if type_id in controlpanels:
        schema = controlpanels[type_id].get('schema', None)
        if schema is None:
            return
        config = registry.for_interface(schema)
        for key, value in payload.items():
            if key in schema:
                config.__setitem__(key, value)
    return
