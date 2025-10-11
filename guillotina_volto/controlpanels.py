from guillotina import schema
from zope.interface import Interface


class IUserGroupSettings(Interface):
    many_groups = schema.Bool(
        title="Many groups?",
        description="Determines if your Plone is optimized for small or large sites. In environments with a lot of groups it can be very slow or impossible to build a list all groups. This option tunes the user interface and behaviour of Plone for this case by allowing you to search for groups instead of listing all of them.",  # noqa
        default=False,
    )
    many_users = schema.Bool(
        title="Many users?",
        description="Determines if your Plone is optimized for small or large sites. In environments with a lot of users it can be very slow or impossible to build a list all users. This option tunes the user interface and behaviour of Plone for this case by allowing you to search for users instead of listing all of them.",  # noqa
        default=False,
    )
