import json

from guillotina.interfaces import IAsyncUtility
from guillotina.interfaces import IFolder
from guillotina.interfaces import IItem
from guillotina.interfaces.content import IContainer
from guillotina.schema import Datetime
from guillotina.schema import JSONField

from guillotina_volto.directives import fieldset_field
from guillotina_volto.fields.image import CloudImageFileField
from guillotina_volto.interfaces.image import IHasImage


RECURRENT_EVENT = json.dumps({"type": "object", "properties": {}})


class ISite(IContainer):
    pass


class IDocument(IFolder):
    pass


class ICMSFolder(IFolder):
    pass


class IBaseFile(IItem):
    pass


class IImage(IBaseFile, IHasImage):

    fieldset_field("image", "default")
    image = CloudImageFileField(title="Image", required=False, widget="file")


class IFile(IBaseFile):
    pass


class IEvent(IItem):

    fieldset_field("start_date", "default")
    start_date = Datetime(title="Start date", required=False, widget="datetime")

    fieldset_field("end_date", "default")
    end_date = Datetime(title="Text", required=False, widget="datetime")

    fieldset_field("recurrent", "default")
    recurrent = JSONField(title="Recurrent", required=False, schema=RECURRENT_EVENT)


class IContentUtility(IAsyncUtility):
    pass
