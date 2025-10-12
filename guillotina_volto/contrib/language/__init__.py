from guillotina import configure
from guillotina.i18n import MessageFactory

_ = MessageFactory("guillotina.contrib.language")

app_settings = {
    "controlpanels": {
        "language": {
            "title": "Language settings",
            "schema": "guillotina_volto.contrib.language.interfaces.ILanguageSettings",
            "group": "general",
        },
    },
    "available_addons": {
        "language": {
            "title": "Multi language addons",
            "dependencies": ""
        }
    }
}

def includeme(root, settings):
    configure.scan("guillotina_volto.contrib.language.subscribers")
    configure.scan("guillotina_volto.contrib.language.content")
    configure.scan("guillotina_volto.contrib.language.interfaces")
    configure.scan("guillotina_volto.contrib.language.install")
    configure.scan("guillotina_volto.contrib.language.behaviors")
    configure.scan("guillotina_volto.contrib.language.api")
