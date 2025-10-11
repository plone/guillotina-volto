from guillotina.interfaces import IFolder
from zope.interface import Interface
from guillotina import schema


class ILanguageFolder(IFolder):
    pass


class ILanguageSettings(Interface):
    available_languages = schema.List(value_type=schema.TextLine())

    default_language = schema.TextLine()

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
