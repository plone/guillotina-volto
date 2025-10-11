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


class ILanguageSettings(Interface):
    available_languages = schema.List(value_type=schema.TextLine())

    default_language = schema.TextLine()

    # Other fields maybe not necessary but sent in the request wyhen
    # patching language in control panel
    set_cookie_always = schema.Bool()
    use_cctld_negotiation = schema.Bool()
    use_combined_language_codes = schema.Bool()
    use_content_negotiation = schema.Bool()
    use_cookie_negotiation = schema.Bool()
    use_path_negotiation = schema.Bool()
    use_request_negotiation = schema.Bool()
    use_subdomain_negotiation = schema.Bool()
    always_show_selector = schema.Bool()
    display_flags = schema.Bool()
