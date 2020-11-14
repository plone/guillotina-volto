from guillotina import configure
from guillotina.utils import get_registry
from guillotina_volto.interfaces import ISite
from guillotina_volto.interfaces import IMenu


@configure.service(
    context=ISite, method='GET', permission='guillotina.ViewContent',
    name='@menu')
async def menu(context, request):

    registry = await get_registry()
    settings = registry.for_interface(IMenu)
    return {
        'value': settings['definition']
    }


@configure.service(
    context=ISite, method='GET', permission='guillotina.ViewContent',
    name='@logo')
async def logo(context, request):

    registry = await get_registry()
    settings = registry.for_interface(IMenu)
    return {
        'value': settings['logo']
    }

