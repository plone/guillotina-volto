# -*- encoding: utf-8 -*-
from guillotina_volto.interfaces.content import ISite
from guillotina import configure
from guillotina.content import Container
from guillotina import addons
from guillotina.content import create_content_in_container
from guillotina.contrib.dbusers.content.users import IUser


@configure.contenttype(
    type_name="Site",
    schema=ISite,
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina.contrib.workflows.interfaces.IWorkflowBehavior",
        "guillotina_volto.interfaces.base.ICMSBehavior",
        "guillotina_volto.interfaces.blocks.IBlocks",
    ],
)
class Site(Container):
    async def install(self):
        await super().install()
        await addons.install(self, "cms")
        await addons.install(self, "dbusers")
        await addons.install(self, "email_validation")
        
        groups = await self.async_get("groups")
        payload = {
            "title":"Managers",
            "groupname":"managers",
            "user_roles": [
                "SiteAdministrator",
            ]
        }
        new_group = await create_content_in_container(
                groups, "Group", "managers", check_security=False, **payload
        )

        users = await self.async_get("users")
        new_user: IUser = await create_content_in_container(
            users, "User", "admin", check_security=False
        )
        new_user.user_groups = ['managers']
        await new_user.set_password("admin")
        new_user.register()
        new_group.users.append(new_user.id)
        new_group.register()
