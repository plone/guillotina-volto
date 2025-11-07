import json

from guillotina import task_vars
from guillotina.component import get_multi_adapter
from guillotina.directives import index
from guillotina.directives import index_field
from guillotina.fields import CloudFileField
from guillotina.interfaces import IAsyncUtility
from guillotina.interfaces import IFolder
from guillotina.interfaces import IItem
from guillotina.interfaces import IResourceSerializeToJson
from guillotina.interfaces.content import IContainer
from guillotina.schema import Datetime
from guillotina.schema import JSONField
from guillotina.schema import TextLine
from guillotina.utils import get_content_path

from guillotina_volto.directives import fieldset_field
from guillotina_volto.fields.image import CloudImageFileField
from guillotina_volto.interfaces.image import IHasImage


RECURRENT_EVENT = json.dumps({"type": "object", "properties": {}})


class ISite(IContainer):
    pass


class IDocument(IFolder):
    pass


class IPage(IFolder):
    pass

class IImage(IItem, IHasImage):
    fieldset_field("image", "default")
    image = CloudImageFileField(title="Image", required=False, widget="file")

    index_field("image_field", store=True, type="text") ## No ho indexa sino hi ha valor, revisar
    image_field = TextLine(title="Image field", required=False, readonly=True, missing_value="image")

@index.with_accessor(IImage, "image_field", type="text", field="image")
async def get_image_field_image_type(ob):
    return "image"

@index.with_accessor(IImage, "image_scales", type="object", field="image")
async def get_image_scales_image_type(ob):
    if ob.image is not None:
        task_request = task_vars.request.get()
        serializer = get_multi_adapter((ob, task_request), IResourceSerializeToJson)
        data = await serializer()
        data["image"]["base_path"] = get_content_path(ob)
        return {"image": [data["image"]]}


class IFile(IItem):
    fieldset_field("file", "default")
    file = CloudFileField(title="File", required=False, widget="file")


class IEvent(IItem):
    fieldset_field("start_date", "default")
    start_date = Datetime(title="Start date", required=False, widget="datetime")

    fieldset_field("end_date", "default")
    end_date = Datetime(title="Text", required=False, widget="datetime")

    fieldset_field("recurrent", "default")
    recurrent = JSONField(title="Recurrent", required=False, schema=RECURRENT_EVENT)


class IContentUtility(IAsyncUtility):
    pass
