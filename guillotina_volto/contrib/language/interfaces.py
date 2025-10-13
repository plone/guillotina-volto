from guillotina import schema
from guillotina.interfaces import IFolder
from zope.interface import Interface

from guillotina_volto.directives import fieldset


class ILanguageFolder(IFolder):
    pass


class ILanguageSettings(Interface):
    fieldset("always_show_selector", "general")
    always_show_selector = schema.Bool(
        title="Always show language selector",
        description="",
        default=False,
    )
    fieldset("authenticated_users_only", "negotiation_scheme")
    authenticated_users_only = schema.Bool(
        title="Authenticated users only",
        description="Related to: use cookie for manual override",
        default=False,
    )
    fieldset("available_languages", "general")
    available_languages = schema.List(
        required=True,
        title="Available languages",
        description="The languages in which the site should be translatable.",
        value_type=schema.Choice(required=True, source="available_languages"),
    )
    fieldset("default_language", "general")
    default_language = schema.Choice(
        title="Site language",
        description="The language used for the content and the UI of this site.",
        required=True,
        source="available_languages",
    )
    fieldset("set_cookie_always", "negotiation_scheme")
    set_cookie_always = schema.Bool(
        title="Set the language cookie always",
        description="i.e. also when the 'set_language' request parameter is absent",
        default=False,
    )
    fieldset("use_cctld_negotiation", "negotiation_scheme")
    use_cctld_negotiation = schema.Bool(
        title="Use top-level domain",
        description="e.g.: www.plone.de",
        default=False,
    )
    fieldset("use_combined_language_codes", "general")
    use_combined_language_codes = schema.Bool(
        title="Show country-specific language variants",
        description="Examples: pt-br (Brazilian Portuguese), en-us (American English) etc.",
        default=True,
    )
    fieldset("use_content_negotiation", "negotiation_scheme")
    use_content_negotiation = schema.Bool(
        title="Use the language of the content item",
        description="Use the language of the content item.",
        default=False,
    )
    fieldset("use_cookie_negotiation", "negotiation_scheme")
    use_cookie_negotiation = schema.Bool(
        title="Use cookie for manual override",
        description="Required for the language selector viewlet to be rendered.",
        default=False,
    )
    fieldset("use_path_negotiation", "negotiation_scheme")
    use_path_negotiation = schema.Bool(
        title="Use language codes in URL path for manual override",
        description="Use language codes in URL path for manual override.",
        default=False,
    )
    fieldset("use_request_negotiation", "negotiation_scheme")
    use_request_negotiation = schema.Bool(
        title="Use browser language request negotiation",
        description="Use browser language request negotiation.",
        default=False,
    )
    fieldset("use_subdomain_negotiation", "negotiation_scheme")
    use_subdomain_negotiation = schema.Bool(
        title="Use subdomain",
        description="e.g.: de.plone.org",
        default=False,
    )
