from guillotina import configure
from guillotina_volto.interfaces.content import ISite
from guillotina.interfaces import IAbsoluteURL
from guillotina.component import getMultiAdapter
from importlib.metadata import version
import platform


@configure.service(
    context=ISite, method="GET", permission="guillotina.AccessContent", name="@system"
)
async def system(context, request):

    url = getMultiAdapter((context, request), IAbsoluteURL)()
    return {
        "id": f"{url}/@system",
        "pil_version": version("pillow"),
        "guillotina": version("guillotina"),
        "guillotina_volto": version("guillotina_volto"),
        "python_version": platform.python_version(),
    }
