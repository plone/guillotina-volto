# -*- coding: utf-8 -*-
from guillotina import configure
from guillotina._cache import FACTORY_CACHE
from guillotina._cache import PERMISSIONS_CACHE
from guillotina.api.service import Service
from guillotina.component import getMultiAdapter
from guillotina.component import query_utility
from guillotina.component import queryUtility
from guillotina.interfaces import IAbsoluteURL
from guillotina_volto.interfaces import ISite
from guillotina.interfaces import IFactorySerializeToJson
from guillotina.interfaces import IPermission
from guillotina.interfaces import IResource
from guillotina.interfaces import IResourceFactory
from guillotina.interfaces import IAsyncContainer
from guillotina.response import HTTPNotFound
from guillotina.utils import get_security_policy
from guillotina.utils import get_current_request
from guillotina.component import get_multi_adapter
from guillotina.api.types import Read

# from guillotina.interfaces import IConstrainTypes
from guillotina_volto.interfaces import ICMSConstrainTypes


@configure.service(
    context=ISite,
    method="GET",
    permission="guillotina.AccessContent",
    name="@types",
    summary="Read information on available types",
    responses={
        "200": {
            "description": "Result results on types",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "@id": {"type": "string"},
                        "title": {"type": "string"},
                        "addable": {"type": "boolean"},
                    },
                },
            },
        }
    },
)
@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.AccessContent",
    name="@types",
    summary="Read information on available types",
    responses={
        "200": {
            "description": "Result results on types",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "@id": {"type": "string"},
                        "title": {"type": "string"},
                        "addable": {"type": "boolean"},
                    },
                },
            },
        }
    },
)
class Types(Service):
    async def __call__(self):
        result = []
        request = get_current_request()
        base_url = IAbsoluteURL(self.context, request)()
        constrains = ICMSConstrainTypes(self.context, None)

        policy = get_security_policy()

        for id, factory in FACTORY_CACHE.items():
            add = True
            if constrains is not None:
                if not constrains.is_type_allowed(id):
                    add = False

            if factory.add_permission:
                if factory.add_permission in PERMISSIONS_CACHE:
                    permission = PERMISSIONS_CACHE[factory.add_permission]
                else:
                    permission = query_utility(IPermission, name=factory.add_permission)
                    PERMISSIONS_CACHE[factory.add_permission] = permission

                if permission is not None and not policy.check_permission(
                    permission.id, self.context
                ):
                    add = False
            if add:
                result.append(
                    {"@id": base_url + "/@types/" + id, "addable": True, "title": id}
                )
        return result


@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.AccessContent",
    name="@types/{type_name}",
    summary="Read information on available types",
    parameters=[{"in": "path", "name": "type_name", "required": True, "schema": {"type": "string"}}],
    responses={
        "200": {
            "description": "Result results on types",
            "content": {"application/json": {"schema": {"properties": {}}}},
        }
    },
)
class Read(Read):
    async def prepare(self):
        type_name = self.request.matchdict["type_name"]
        self.value = query_utility(IResourceFactory, name=type_name)
        if self.value is None:
            raise HTTPNotFound(content={"reason": f"Could not find type {type_name}", "type_name": type_name})

    async def __call__(self):
        return await super().__call__()
