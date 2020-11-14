from guillotina import configure
from guillotina.utils import get_registry
from guillotina_volto.interfaces import ISite
from guillotina_volto.interfaces import ICustomTheme
from guillotina.response import Response


@configure.service(
    context=ISite, method='GET', permission='guillotina.ViewContent',
    name='@css')
async def themecss(context, request):

    registry = await get_registry()
    settings = registry.for_interface(ICustomTheme)
    resp = Response(status=200)
    resp.content_type = 'text/css'
    disposition = 'filename="style.css"'
    resp.headers["CONTENT-DISPOSITION"] = disposition
    resp.content_length = len(settings['css'])
    await resp.prepare(request)
    await resp.write(settings['css'].encode(), eof=True)
    return resp

