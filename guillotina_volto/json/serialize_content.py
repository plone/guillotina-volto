from guillotina import configure
from guillotina.behaviors.attachment import IAttachmentMarker
from guillotina.interfaces import IAbsoluteURL
from guillotina.interfaces import IResource
from guillotina.interfaces import IResourceSerializeToJson
from guillotina.interfaces import IResourceSerializeToJsonSummary
from guillotina.json.serialize_content import SerializeToJson
from guillotina.json.serialize_value import json_compatible

from guillotina_volto.interfaces import ICMSLayer


@configure.adapter(
    for_=(IResource, ICMSLayer), provides=IResourceSerializeToJsonSummary
)
class DefaultJSONSummarySerializer(object):
    """Default ISerializeToJsonSummary adapter.

    Requires context to be adaptable to IContentListingObject, which is
    the case for all content objects providing IResource.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    async def __call__(self):

        summary = json_compatible(
            {
                "@id": IAbsoluteURL(self.context)(),
                "@type": self.context.type_name,
                "@name": self.context.__name__,
                "@uid": self.context.uuid,
                "UID": self.context.uuid,
                "title": self.context.title,
            }
        )
        return summary


@configure.adapter(for_=(IAttachmentMarker, ICMSLayer), provides=IResourceSerializeToJson)
class FileJSONSerializer(SerializeToJson):
    async def __call__(self, include=[], omit=[]):
        data = await super().__call__(include=include, omit=omit)
        bdata = data.get("guillotina.behaviors.attachment.IAttachment")
        if bdata:
            fdata = bdata.get("file")
            if fdata:
                data["file"] = fdata
                data["file"]["download"] = "{}/@download/file/{}".format(
                    IAbsoluteURL(self.context)(), data["file"]["filename"]
                )
        return data
