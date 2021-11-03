from guillotina import configure
from guillotina import app_settings
from guillotina.api.content import resolve_uid
from guillotina.api.service import Service
from guillotina.component import query_utility
from guillotina.content import duplicate, move
from guillotina.event import notify
from guillotina.events import ObjectPermissionsViewEvent
from guillotina.interfaces import Deny
from guillotina.interfaces import IAsyncContainer
from guillotina.interfaces import ICatalogUtility
from guillotina.interfaces import IInheritPermissionMap
from guillotina.interfaces import IRolePermissionMap
from guillotina.interfaces import IPrincipalPermissionMap
from guillotina.interfaces import IPrincipalRoleMap
from guillotina.interfaces import IResource
from guillotina_volto.interfaces import ICMSLayer
from guillotina_volto.interfaces import ISite
from guillotina.response import HTTPPreconditionFailed
from guillotina.response import HTTPServiceUnavailable
from guillotina.security.utils import apply_sharing
from guillotina.utils import find_container
from guillotina.utils import get_object_by_uid
from guillotina.utils import get_security_policy, get_object_url
from guillotina.utils import iter_parents
from guillotina.utils import navigate_to


@configure.service(
    method="GET",
    name="resolveuid/{uid}",
    context=ISite,
    permission="guillotina.AccessContent",
    summary="Get content by UID",
    responses={"200": {"description": "Successful"}},
)
async def plone_resolve_uid(context, request):
    """
    b/w compatible plone endpoint name
    """
    return await resolve_uid(context, request)


MAX_FOLDER_SORT_SIZE = 5000


# @configure.service(
#     context=IAsyncContainer, method='PATCH',
#     permission='guillotina.ModifyContent', name='@order')
# class OrderContent(Service):
#     order = None
#     mapped = None
#     subset_ids = None
#     obj_id = None
#     delta = None

#     def __init__(self, context, request):
#         super().__init__(context, request)
#         self.order = []
#         self.mapped = {}

#     async def validate(self):
#         # verify current order matches
#         txn = get_transaction()
#         if not supports_ordering(txn.storage):
#             raise HTTPBadRequest(content={
#                 'message': 'Content ordering not supported'
#             })

#         conn = await txn.get_connection()
#         results = await conn.fetch('''
#     select id, (json->>'position_in_parent')::int as pos from {}
#     WHERE parent_id = $1 AND of IS NULL
#     ORDER BY (json->>'position_in_parent')::int ASC
#     limit {}'''.format(
#             txn.storage._objects_table_name, MAX_FOLDER_SORT_SIZE), self.context.__uuid__)
#         if len(results) >= MAX_FOLDER_SORT_SIZE:
#             raise HTTPPreconditionFailed(content={
#                 'message': 'Content ordering not supported on folders larger than {}'.format(
#                     MAX_FOLDER_SORT_SIZE
#                 )
#             })

#         results.sort(key=lambda item: item['pos'] or 0)
#         for item in results:
#             self.order.append(item['id'])
#             self.mapped[item['id']] = item['pos']

#         if len(self.subset_ids) > len(self.order):
#             raise HTTPPreconditionFailed(content={
#                 'message': 'Invalid subset. More values than current ordering'
#             })
#         if len(self.subset_ids) == len(self.order):
#             if self.subset_ids != self.order:
#                 raise HTTPPreconditionFailed(content={
#                     'message': 'Invalid subset',
#                     'current': self.order
#                 })
#         else:
#             # verify subset
#             # find current ordered subset
#             try:
#                 start = self.order.index(self.subset_ids[0])
#                 end = self.order.index(self.subset_ids[-1]) + 1
#             except ValueError:
#                 raise HTTPPreconditionFailed(content={
#                     'message': 'Invalid subset. Could not calculate subset match',

#                 })
#             order_subset = self.order[start:end]
#             if self.subset_ids != order_subset:
#                 raise HTTPPreconditionFailed(content={
#                     'message': 'Invalid subset',
#                     'current': order_subset
#                 })

#         if ((self.order.index(self.obj_id) + self.delta + 1) > len(self.order) or (
#                 self.order.index(self.obj_id) + self.delta) < 0):
#             raise HTTPPreconditionFailed(content={
#                 'message': 'Can not move. Invalid move target.'
#             })

#     async def swap(self, two):
#         one = self.obj_id
#         one_pos = self.mapped[one]
#         two_pos = self.mapped[two]

#         ob_one = await self.context.async_get(one)
#         ob_two = await self.context.async_get(two)

#         beh_one = await get_behavior(ob_one, ICMSBehavior)
#         beh_two = await get_behavior(ob_two, ICMSBehavior)

#         import pdb; pdb.set_trace()
#         beh_one.position_in_parent = two_pos
#         beh_two.position_in_parent = one_pos

#         one_idx = self.order.index(one)
#         two_idx = self.order.index(two)
#         self.order[two_idx], self.order[one_idx] = self.order[one_idx], self.order[two_idx]

#         await index.index_object(ob_one, indexes=['position_in_parent'], modified=True)
#         await index.index_object(ob_two, indexes=['position_in_parent'], modified=True)
#         return {
#             one: {
#                 'idx': two_idx,
#                 'pos': two_pos
#             },
#             two: {
#                 'idx': one_idx,
#                 'pos': one_pos
#             }
#         }

#     async def __call__(self):
#         data = await self.request.json()
#         self.subset_ids = data['subset_ids']
#         self.obj_id = data['obj_id']
#         self.delta = data['delta']

#         await self.validate()

#         # now swap position for item
#         moved_item_index = self.order.index(self.obj_id)
#         moved = {}
#         # over range of delta and shift position of the rest the opposite direction
#         # for example:
#         #  - move idx 0, delta 3
#         #    - idx 1, 2, 3 are moved to 0, 1, 2
#         #  - move idx 4, delta -2
#         #    - idx 2, 3 are moved to 3, 4
#         if self.delta < 0:
#             group = [i for i in reversed(
#                 self.order[moved_item_index + self.delta:moved_item_index + 1])]
#         else:
#             group = self.order[moved_item_index:moved_item_index + self.delta + 1]

#         for item_id in group[1:]:
#             moved.update(await self.swap(item_id))

#         return moved


async def _iter_copyable_content(context, request):
    policy = get_security_policy()
    data = await request.json()
    if "source" not in data:
        raise HTTPPreconditionFailed(content={"reason": "No source"})

    source = data["source"]
    if not isinstance(source, list):
        source = [source]

    container = find_container(context)
    container_url = get_object_url(container)
    for item in source:
        if item.startswith(container_url):
            path = item[len(container_url) :]
            ob = await navigate_to(container, path.strip("/"))
            if ob is None:
                raise HTTPPreconditionFailed(
                    content={"reason": "Could not find content", "source": item}
                )
        elif "/" in item:
            ob = await navigate_to(container, item.strip("/"))
            if ob is None:
                raise HTTPPreconditionFailed(
                    content={"reason": "Could not find content", "source": item}
                )
        else:
            try:
                ob = await get_object_by_uid(item)
            except KeyError:
                raise HTTPPreconditionFailed(
                    content={"reason": "Could not find content", "source": item}
                )
        if not policy.check_permission("guillotina.DuplicateContent", ob):
            raise HTTPPreconditionFailed(
                content={"reason": "Invalid permission", "source": item}
            )
        yield ob


@configure.service(
    method="POST",
    name="@copy_mult",
    context=IAsyncContainer,
    permission="guillotina.AddContent",
    summary="Copy data into destintation",
    parameteres=[
        {
            "name": "body",
            "in": "body",
            "type": "object",
            "schema": {
                "properties": {"source": {"type": "array", "items": {"type": "string"}}}
            },
            "required": ["source"],
        }
    ],
    responses={"200": {"description": "Successful"}},
)
async def copy_content(context, request):
    results = []
    async for ob in _iter_copyable_content(context, request):
        new_ob = await duplicate(ob, context)
        results.append({"source": get_object_url(ob), "target": get_object_url(new_ob)})
    return results


@configure.service(
    method="POST",
    name="@move_mult",
    context=IAsyncContainer,
    permission="guillotina.AddContent",
    summary="Move data into destintation",
    parameteres=[
        {
            "name": "body",
            "in": "body",
            "type": "object",
            "schema": {
                "properties": {"source": {"type": "array", "items": {"type": "string"}}}
            },
            "required": ["source"],
        }
    ],
    responses={"200": {"description": "Successful"}},
)
async def move_content(context, request):
    results = []
    async for ob in _iter_copyable_content(context, request):
        new_ob = await move(ob, context)
        results.append({"source": get_object_url(ob), "target": get_object_url(new_ob)})
    return results


async def get_all_sharing_roles():
    all_roles = list()
    restrict_roles = app_settings.get('sharing_tab_roles', list())
    roles = configure.get_configurations('guillotina', 'role')
    for app_name in app_settings.get('applications', list()):
        roles += configure.get_configurations(app_name, 'role')

    for _type, role_config in roles:
        role_id = role_config['config'].get('id')
        role_description = role_config['config'].get('description')
        if not role_description:
            continue
        if restrict_roles:
            if role_id in restrict_roles:
                all_roles.append({
                    'id': role_id,
                    'title': role_description
                })
        else:
            all_roles.append({
                'id': role_id,
                'title': role_description
            })
    return all_roles


@configure.service(
    context=IResource,
    layer=ICMSLayer,
    method="GET",
    permission="guillotina.SeePermissions",
    name="@sharing"
)

class SharingGET(Service):

    async def set_roles_for_context(self, context, acquired=False):
        prinrole = IPrincipalRoleMap(context)
        for pr_id, permissions in prinrole._bycol.items():
            local_roles = [
                p for p,s in permissions.items()
                if s.get_name() == 'Allow' and p in self.all_role_ids
            ]
            # If none of the local roles are configurable from the sharing tab,
            # just go to the next principal
            if not local_roles:
                continue

            local_roles_dict = dict()
            for role in self.all_role_ids:
                if role in local_roles:
                    if acquired:
                        local_roles_dict[role] = "acquired"
                    else:
                        local_roles_dict[role] = True
                else:
                    local_roles_dict[role] = False

            if pr_id in self.users_with_local_roles:
                user_value = self.users_with_local_roles[pr_id]
                existing_roles = user_value.get('roles', dict())
                for k,v in local_roles_dict.items():
                    if v and existing_roles.get(k) != "global":
                        if acquired:
                            existing_roles[k] = "acquired"
                        else:
                            existing_roles[k] = True
                user_value['roles'] = existing_roles
                self.users_with_local_roles[pr_id] = user_value

            elif pr_id in self.groups_with_local_roles:
                group_value = self.groups_with_local_roles[pr_id]
                existing_roles = group_value.get('roles', dict())
                for k,v in local_roles_dict.items():
                    if v and existing_roles.get(k) != "global":
                        if acquired:
                            existing_roles[k] = "acquired"
                        else:
                            existing_roles[k] = True
                group_value['roles'] = existing_roles
                self.groups_with_local_roles[pr_id] = group_value

            else:
                query = {
                    'portal_type__or': 'Group,User',
                    'id': pr_id,
                }
                groups_or_users = await self.search.search(self.site, query)
                for item in groups_or_users.get('items', list()):
                    if item['type_name'] == 'User':
                        for role in local_roles_dict.keys():
                            if role in item['user_roles']:
                                local_roles_dict[role] = "global"
                        user_id = item.get('id')
                        user_name = item.get('user_name')
                        if not user_name:
                            user_name = user_id
                        else:
                            user_name += f' ({user_id})'
                        entry = {
                            "disabled": False,
                            "id": user_id,
                            "login": user_id,
                            "roles": local_roles_dict,
                            "title": user_name,
                            "type": "user"
                        }
                        self.users_with_local_roles[pr_id] = entry
                    elif item['type_name'] == 'Group':
                        for role in local_roles_dict.keys():
                            if role in item['group_user_roles']:
                                local_roles_dict[role] = "global"
                        group_id = item.get('id')
                        group_name = item.get('group_name')
                        if not group_name:
                            group_name = group_id
                        else:
                            group_name += f' ({group_id})'
                        entry = {
                            "disabled": False,
                            "id": group_id,
                            "login": None,
                            "roles": local_roles_dict,
                            "title": group_name,
                            "type": "group"
                        }
                        self.groups_with_local_roles[pr_id] = entry


    async def __call__(self, changed=False):
        """Change permissions"""
        context = self.context
        request = self.request

        # Find site root
        self.site = context
        while not ISite.providedBy(self.site):
            self.site = self.site.__parent__

        self.search = query_utility(ICatalogUtility)
        self.users_with_local_roles = dict()
        self.groups_with_local_roles = dict()

        # Find all available roles
        self.all_roles = await get_all_sharing_roles()
        self.all_role_ids = [i['id'] for i in self.all_roles]

        inherit_permissions = IInheritPermissionMap(context)

        inherit = True
        if inherit_permissions is not None:
            settings = inherit_permissions.get_locked_permissions()
            # Either all permissions are allowed to be inherited or none are
            for (p, s) in settings:
                if p in self.all_role_ids and s is Deny:
                    inherit = False

        result = {
            "available_roles": self.all_roles,
            "entries": list(),
            "inherit": inherit
        }

        await self.set_roles_for_context(context)

        if inherit:
            for obj in iter_parents(context):
                roleperm = IRolePermissionMap(obj, None)
                url = get_object_url(obj, request)
                if roleperm is not None and url is not None:
                    await self.set_roles_for_context(obj, acquired=True)

        group_keys = list(self.groups_with_local_roles.keys())
        group_keys.sort()

        user_keys = list(self.users_with_local_roles.keys())
        user_keys.sort()

        for k in group_keys:
            result['entries'].append(self.groups_with_local_roles[k])

        for k in user_keys:
            result['entries'].append(self.users_with_local_roles[k])

        # Finally, add results for searched users/groups
        search_query = request.query.get('search', None)
        if search_query:
            site = context
            while not ISite.providedBy(site):
                site = site.__parent__

            search = query_utility(ICatalogUtility)
            if search:
                # find groups
                query = {
                    'portal_type': 'Group',
                    'title__in': search_query,
                }

                groups = await search.search(site, query)
                for group in groups.get('items', list()):
                    group_id = group.get('id')
                    if group_id not in self.groups_with_local_roles:
                        group_name = group.get('group_name')
                        if not group_name:
                            group_name = group_id
                        else:
                            group_name += f' ({group_id})'
                        entry = {
                            "disabled": False,
                            "id": group_id,
                            "login": None,
                            "roles": dict(),
                            "title": group_name,
                            "type": "group"
                        }
                        for roleid in self.all_role_ids:
                            if roleid in group.get('group_user_roles', list()):
                                entry['roles'][roleid] = "global"
                            else:
                                entry['roles'][roleid] = False

                        result['entries'].append(entry)

                # find users
                query = {
                    'portal_type': 'User',
                    'title__in': search_query,
                }
                users = await search.search(site, query)
                for user in users.get('items', list()):
                    user_id = user.get('id')
                    if user_id not in self.users_with_local_roles:
                        user_name = user.get('user_name')
                        if not user_name:
                            user_name = user_id
                        else:
                            user_name += f' ({user_id})'
                        entry = {
                            "disabled": False,
                            "id": user_id,
                            "login": user_id,
                            "roles": dict(),
                            "title": user_name,
                            "type": "user"
                        }
                        for roleid in self.all_role_ids:
                            if roleid in user.get('user_roles', list()):
                                entry['roles'][roleid] = "global"
                            else:
                                entry['roles'][roleid] = False

                        result['entries'].append(entry)

        return result


@configure.service(
    context=IResource,
    layer=ICMSLayer,
    method="POST",
    permission="guillotina.ChangePermissions",
    name="@sharing",
    summary="Change permissions for a resource",
    validate=True
)
class SharingPOST(Service):
    async def __call__(self, changed=False):
        """Change permissions"""
        context = self.context
        request = self.request
        data = await request.json()

        if 'entries' not in data:
            raise PreconditionFailed(self.context, "entries missing")

        entries = data['entries']

        prinrole = list()
        for entry in entries:
            principal = entry.get('id')
            for k,v in entry['roles'].items():
                setting = None
                if v is True:
                    setting = "Allow"
                if v is False:
                    setting = "Unset"
                if setting:
                    prinrole.append({
                        "principal": principal,
                        "role": k,
                        "setting": setting
                    })

        self.all_roles = await get_all_sharing_roles()
        self.all_role_ids = [i['id'] for i in self.all_roles]

        # When 'inherit' is not in data, means the value should be enabled
        inherit = data.get('inherit', True)

        perminhe = list()
        for role_id in self.all_role_ids:
            perminhe.append({
                'permission': role_id,
                'setting': 'Allow' if inherit else 'Deny'
            })

        data_to_apply = {'perminhe': perminhe}

        if prinrole:
            data_to_apply = {"prinrole": prinrole}

        return await apply_sharing(context, data_to_apply)
