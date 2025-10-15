import json

from guillotina import schema
from zope.interface import Interface

from guillotina_volto.utils import get_default_logo


MENU_LAYOUT = json.dumps({"type": "object", "properties": {}})

LAYOUT_TYPE_COMPONENTS = json.dumps(
    {
        "type": "object",
        "properties": {},
        "additionalProperties": {
            "type": "array",
            "items": {"type": "object", "properties": {"id": {"type": "string"}}},
        },
    }
)


class IImagingSettings(Interface):
    allowed_sizes = schema.Dict(
        title="Allowed image sizes",
        description="Specify all allowed maximum image dimensions, one per line. The required format is &lt;name&gt; &lt;width&gt;:&lt;height&gt;.",  # noqa
        hide_in_fieldset=True,
        missing_value={
            "high": "1400:1400",
            "large": "768:768",
            "preview": "400:400",
            "mini": "200:200",
            "thumb": "128:128",
            "tile": "64:64",
            "icon": "32:32",
        },
    )

    quality = schema.Int(
        default=88,
        required=True,
        title="Scaled image quality",
        description="A value for the quality of scaled images, from 1 (lowest) to 95 (highest). A value of 0 will mean plone.scaling's default will be used, which is currently 88.",  # noqa
    )


class IMenu(Interface):

    definition = schema.JSONField(title="Menu definition", required=False, schema=MENU_LAYOUT, defaultFactory=list)

    logo = schema.Text(title="Logo", required=False, defaultFactory=get_default_logo)


class ICustomTheme(Interface):

    css = schema.Text(title="CSS Text", required=False, default="")


class ILayoutComponents(Interface):

    components = schema.JSONField(
        title="Layout enabled components by type",
        required=False,
        schema=LAYOUT_TYPE_COMPONENTS,
        defaultFactory=dict,
    )


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
