from zope.interface import Interface
from guillotina.directives import index
from guillotina.directives import index_field
from guillotina_volto.directives import fieldset_field
from guillotina.schema import JSONField
from guillotina.schema import TextLine
from guillotina.interfaces.content import IResource
from guillotina.utils import get_behavior


class IHasImage(Interface):
    pass

class IHasImagePreview(Interface):
    pass

class IImagePreviewLinkAttachment(Interface):
    index_field("preview_caption_link", store=True, type="text")
    fieldset_field("preview_caption_link", "preview_image")
    preview_caption_link = TextLine(title="Preview image caption", required=False)
    index_field("preview_image_link", store=True, type="object")
    fieldset_field("preview_image_link", "preview_image")
    preview_image_link = JSONField(
        title="Preview image",
        description="Select an image that will be used in listing and teaser blocks.",
        required=False,
        widgetOptions={
            "frontendOptions": {"widget": "object_browser", "widgetProps": {"mode": "image", "return": "single"}}
        },
    )

@index.with_accessor(
    IResource, "image_field", behavior="guillotina_volto.interfaces.image.IImagePreviewLinkAttachment", type="text", field="preview_image_link")
async def get_image_field(ob):
    return "preview_image_link"

@index.with_accessor(
    IResource, "image_scales", behavior="guillotina_volto.interfaces.image.IImagePreviewLinkAttachment", type="object", field="preview_image_link")
async def get_image_scales(ob):
    bhr = await get_behavior(ob, IImagePreviewLinkAttachment)
    if bhr.preview_image_link is not None and "image_scales" in bhr.preview_image_link:
        return {"preview_image_link": [bhr.preview_image_link["image_scales"]["image"][0]]}

@index.with_accessor(
    IResource, "hasPreviewImage", behavior="guillotina_volto.interfaces.image.IImagePreviewLinkAttachment", type="boolean", field="preview_image_link")
async def get_has_preview_image(ob):
    bhr = await get_behavior(ob, IImagePreviewLinkAttachment)
    return bhr.preview_image_link is not None