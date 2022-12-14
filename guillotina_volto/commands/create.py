from guillotina import addons
from guillotina import task_vars
from guillotina.commands import Command
from guillotina.component import get_utility
from guillotina.content import create_content_in_container
from guillotina.contrib.dbusers.content.users import IUser
from guillotina.contrib.workflows.interfaces import IWorkflow
from guillotina.event import notify
from guillotina.events import BeforeObjectRemovedEvent
from guillotina.events import ObjectRemovedEvent
from guillotina.exceptions import ConflictIdOnContainer
from guillotina.interfaces import IApplication
from guillotina.interfaces import IDatabase
from guillotina.transactions import transaction


class CMSCreateCommand(Command):
    description = "Guillotina volto db initiliazation"

    def get_parser(self):
        parser = super(CMSCreateCommand, self).get_parser()
        parser.add_argument("-d", "--db", help="Database", required=True)
        parser.add_argument("-n", "--name", help="CMS container id", required=True)
        parser.add_argument(
            "--force",
            dest="force",
            action="store_true",
            help="Delete container if exists",
            required=False,
        )
        return parser

    async def create(self, arguments, db):

        if arguments.force:
            async with transaction(db=db) as txn:
                tm = task_vars.tm.get()
                root = await tm.get_root(txn=txn)
                if await root.async_contains(arguments.name):
                    context = await root.async_get(arguments.name)
                    content_id = context.id
                    parent = context.__parent__
                    await notify(BeforeObjectRemovedEvent(context, parent, content_id))
                    txn.delete(context)
                    await notify(ObjectRemovedEvent(context, parent, content_id))

        site = None
        async with transaction(db=db) as txn:
            tm = task_vars.tm.get()
            root = await tm.get_root(txn=txn)
            try:
                site = await create_content_in_container(
                    root, "Site", arguments.name, check_security=False
                )
                await addons.install(site, "cms")
                await addons.install(site, "dbusers")

                workflow = IWorkflow(site)
                await workflow.do_action("publish", "Initial setup")
            except ConflictIdOnContainer:
                pass

        if site is None:
            return

        async with transaction(db=db) as txn:
            await txn.refresh(site)
            groups = await site.async_get("groups")
            obj = await create_content_in_container(
                groups, "Group", "Managers", check_security=False
            )
            obj.user_roles = [
                "guillotina.Manager",
                "guillotina.ContainerAdmin",
                "guillotina.Owner",
            ]
            obj.register()

        async with transaction(db=db) as txn:
            await txn.refresh(site)
            users = await site.async_get("users")
            obj: IUser = await create_content_in_container(
                users, "User", "admin", check_security=False
            )
            await obj.set_password("admin")
            obj.groups = ["Managers"]

    async def run(self, arguments, settings, app):
        root = get_utility(IApplication, name="root")
        if arguments.db in root:
            db = root[arguments.db]
            if IDatabase.providedBy(db):
                print(f"Creating container: {arguments.name}")
                await self.create(arguments, db)
