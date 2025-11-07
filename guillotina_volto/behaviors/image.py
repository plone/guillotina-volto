from guillotina import configure
from guillotina import schema
from guillotina.fields import CloudFileField
from guillotina.interfaces import IResource
from zope.interface import Interface
from guillotina.behaviors.properties import ContextProperty

from guillotina.behaviors.instance import AnnotationBehavior
from guillotina_volto.interfaces import IHasImage, IImagePreviewLinkAttachment, IHasImagePreview


@configure.behavior(title="Image attachment", for_=IResource, marker=IHasImage)
class IImageAttachment(Interface):
    image = CloudFileField()
    caption = schema.TextLine()


@configure.behavior(title="Lead image attachment", for_=IResource, marker=IHasImage)
class ILeadImage(Interface):
    lead = CloudFileField()

@configure.behavior(
    title="Image preview link behavior",
    provides=IImagePreviewLinkAttachment,
    for_="guillotina.interfaces.IResource",
    marker=IHasImagePreview
)
class ImagePreviewLinkAttachment(AnnotationBehavior):
    preview_caption_link = ContextProperty("preview_caption_link", "")
    preview_image_link = ContextProperty("preview_image_link", None)