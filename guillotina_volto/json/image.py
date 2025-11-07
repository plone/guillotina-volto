from guillotina import configure
from guillotina import task_vars
from guillotina.files.field import deserialize_cloud_field
from guillotina.utils import get_current_request
from guillotina.utils import get_url
from guillotina.utils import to_str
from zope.interface import alsoProvides
from guillotina.utils import get_content_path

from guillotina_volto.fields.interfaces import ICloudImageFileField
from guillotina_volto.fields.interfaces import IImageFile
from guillotina_volto.interfaces import IImagingSettings


def get_image_data(value, context):
    base_path = ""
    request = get_current_request()
    if context is not None:
        base_path = get_content_path(context)
    else:
        base_path = get_url(request, request.path)

    registry = task_vars.registry.get()
    settings = registry.for_interface(IImagingSettings)
    scales = {}

    # if request.method == "POST":
    #     import pdb; pdb.set_trace()
    # if request.method == "POST" and context is None:
    #     base_path = base_path + "/" + value.filename.lower().replace(" ", "-")
    # TODO: VIRUALHOSTMONSTER
    for size, dimension in settings["allowed_sizes"].items():
        width, _, height = dimension.partition(":")
        scales[size] = {
            "download": base_path + "/@@images/image/" + size,
            "height": height,
            "width": width,
        }

    return {
        "filename": value.filename,
        "content_type": to_str(value.content_type),
        "size": value.size,
        "extension": value.extension,
        "md5": value.md5,
        "download": f"{base_path}/@download/image",
        "scales": scales,
        "base_path": base_path,
    }

@configure.value_serializer(for_=IImageFile)
async def json_converter(value):
    if value is None:
        return value

    return get_image_data(value, None)


@configure.value_deserializer(ICloudImageFileField)
async def deserialize_image_cloud_field(field, value, context):
    val = await deserialize_cloud_field(field, value, context)
    if val is not None:
        alsoProvides(val, IImageFile)
    return val
