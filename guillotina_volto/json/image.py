from guillotina import configure
from guillotina import task_vars
from guillotina.files.field import deserialize_cloud_field
from guillotina.utils import get_current_request
from guillotina.utils import to_str
from guillotina_volto.fields.interfaces import ICloudImageFileField
from guillotina_volto.fields.interfaces import IImageFile
from guillotina_volto.interfaces import IImagingSettings
from zope.interface import alsoProvides
from guillotina.utils import get_url


@configure.value_serializer(for_=IImageFile)
def json_converter(value):
    if value is None:
        return value

    request = get_current_request()
    registry = task_vars.registry.get()
    settings = registry.for_interface(IImagingSettings)
    scales = {}
    url = get_url(request, request.path)
    # TODO: VIRUALHOSTMONSTER
    for size, dimension in settings["allowed_sizes"].items():
        width, _, height = dimension.partition(":")
        scales[size] = {
            "download": url + "/@@images/image/" + size,
            "height": height,
            "width": width,
        }

    return {
        "filename": value.filename,
        "content_type": to_str(value.content_type),
        "size": value.size,
        "extension": value.extension,
        "md5": value.md5,
        "download": f"{url}/@download/image",
        "scales": scales,
    }


@configure.value_deserializer(ICloudImageFileField)
async def deserialize_image_cloud_field(field, value, context):
    val = await deserialize_cloud_field(field, value, context)
    if val is not None:
        alsoProvides(val, IImageFile)
    return val
