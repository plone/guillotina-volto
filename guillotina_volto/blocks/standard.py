from guillotina import schema
from guillotina_volto import guillotina_volto
from zope.interface import Interface
from guillotina.schema import JSONField
import json


@guillotina_volto.block(
    name='title', title='title'
)
class IBlockTitle(Interface):
    title = schema.TextLine(required=True)


@guillotina_volto.block(
    name='description', title='Description'
)
class IBlockDescription(Interface):
    description = schema.TextLine(required=True)


TEXT_SCHEMA = json.dumps({
    'type': 'object',
    'properties': {
        'content-type': {'type': 'string'},
        'text': {'type': 'string'},
        'data': {'type': 'string'}
    }
})


@guillotina_volto.block(
    name='text', title='Text'
)
class IBlockText(Interface):
    text = JSONField(
        schema=TEXT_SCHEMA
    )

    description = schema.TextLine()


@guillotina_volto.block(
    name='image', title='Image'
)
class IBlockImage(Interface):
    url = schema.TextLine()


@guillotina_volto.block(
    name='video', title='Video'
)
class IBlockVideo(Interface):
    url = schema.TextLine()
