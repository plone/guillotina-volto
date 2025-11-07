from guillotina import configure
from guillotina.interfaces import IAbsoluteURL
from guillotina.interfaces import IResource
from guillotina.interfaces import IResourceSerializeToJson
from guillotina.interfaces import IResourceSerializeToJsonSummary
from guillotina.interfaces.json import IValueToJson
from guillotina.json.serialize_content import SerializeToJson
from guillotina.profile import profilable
from guillotina.utils import get_content_path
from guillotina.component import query_adapter, get_adapter
from guillotina_volto.fields.interfaces import IImageFile
from guillotina_volto.json.image import get_image_data
from guillotina_volto.interfaces import ICMSLayer
from guillotina_volto.interfaces import IFile
from guillotina_volto.interfaces import IImage
from guillotina_volto.interfaces.image import IHasImagePreview
from guillotina.utils import get_behavior
from guillotina_volto.interfaces.image import IImagePreviewLinkAttachment, IHasImage
from guillotina.utils import apply_coroutine
import logging
import asyncio

logger = logging.getLogger("guillotina")

class ContextAwareValue:
    def __init__(self, value, context):
        self.value = value
        self.context = context

@configure.adapter(for_=ContextAwareValue, provides=IValueToJson)
def context_aware_serializer(context_aware_value):
    value = context_aware_value.value
    context = context_aware_value.context
    
    if IImageFile.providedBy(value):
        return get_image_data(value, context)

    return query_adapter(value, IValueToJson, default=_MISSING)

_MISSING = object()
@profilable
def json_compatible(value, context=None):
    if value is None:
        return value

    type_ = type(value)
    if type_ in (str, bool, int, float):
        return value
    
    if context is not None:
        context_aware = ContextAwareValue(value, context)
        result_value = get_adapter(context_aware, IValueToJson)
    else:
        result_value = query_adapter(value, IValueToJson, default=_MISSING)
    if result_value is _MISSING:
        raise TypeError("No converter for making" " {0!r} ({1}) JSON compatible.".format(value, type(value)))
    else:
        return result_value


@configure.adapter(for_=(IResource, ICMSLayer), provides=IResourceSerializeToJsonSummary)
class DefaultJSONSummarySerializer(object):
    """Default ISerializeToJsonSummary adapter.

    Requires context to be adaptable to IContentListingObject, which is
    the case for all content objects providing IResource.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    async def __call__(self):
        data = {
            "@id": IAbsoluteURL(self.context)(),
            "@type": self.context.type_name,
            "@name": self.context.__name__,
            "@uid": self.context.uuid,
            "UID": self.context.uuid,
            "title": self.context.title,
        }
        if IHasImagePreview.providedBy(self.context):
            bhr = await get_behavior(self.context, IImagePreviewLinkAttachment)
            if bhr.preview_image_link is not None and "image_scales" in bhr.preview_image_link:
                image_data = bhr.preview_image_link["image_scales"]["image"][0]
                data['preview_image_link'] = image_data
                data["image_scales"] = {"preview_image_link": [image_data]}
                data["image_field"] = "preview_image_link"
        elif IImage.providedBy(self.context):
            image_data = get_image_data(self.context.image, self.context)
            data['image'] = image_data
            data["image_scales"] = {"image": [image_data]}
            data["image_field"] = "image"
        return json_compatible(data, self.context)


@configure.adapter(for_=(IFile, ICMSLayer), provides=IResourceSerializeToJson)
class FileJSONSerializer(SerializeToJson):
    async def __call__(self, include=[], omit=[]):
        data = await super().__call__(include=include, omit=omit)
        if data.get("file"):
            data["file"]["download"] = "{}/@download/file/{}".format(
                IAbsoluteURL(self.context)(), data["file"]["filename"]
            )
        return data

@configure.adapter(for_=(IResource, ICMSLayer), provides=IResourceSerializeToJson)
class SerializeResourceToJson(SerializeToJson):
    @profilable
    async def serialize_field(self, context, field, default=None):
        try:
            value = await apply_coroutine(field.get, context)
        except Exception:
            logger.warning(
                f"Could not find value for schema field" f"({field.__name__}), falling back to getattr"
            )
            value = getattr(context, field.__name__, default)
        result = json_compatible(value, context)
        if asyncio.iscoroutine(result):
            result = await result
        return result
# @configure.adapter(for_=(IImage, ICMSLayer), provides=IResourceSerializeToJsonSummary)
# class SerializeFolderToJson(SerializeResourceToJson):
#     @profilable
#     async def __call__(self, include=None, omit=None):
#         include = include or []
#         omit = omit or []
#         result = await super(SerializeResourceToJson, self).__call__(include=include, omit=omit)
#         if "image" in result  and "scales" in result['image']:
#             new_image_data = result['image']
#             result["image_scales"] = {"image": [new_image_data]}
#             result["image_field"] = "image"
#         return result
    