# -*- coding: utf-8 -*-
import glob

import yaml
from guillotina import configure
from guillotina.i18n import MessageFactory


_ = MessageFactory("guillotina_volto")

app_settings = {
    "applications": [
        "guillotina.contrib.catalog.pg",
        "guillotina.contrib.swagger",
        "guillotina.contrib.dbusers",
    ],
    "available_blocks": {},
    "commands": {"create-container": "guillotina_volto.commands.create.CMSCreateCommand"},
    "available_roles": [
        "guillotina.Contributor",
        "guillotina.Editor",
        "guillotina.Reader",
        "guillotina.Reviewer",
        "guillotina.Owner"
    ],
    "layouts": {
        "CMSFolder": [
            "listing_view",
            "tabular_view",
            "summary_view",
            "layout_view",
            "full_view",
            "album_view",
            "event_listing",
            "document_view",
        ],
        "Document": ["document_view", "layout_view", "default"],
        "Site": ["document_view", "layout_view", "default"],
        "News": ["document_view", "layout_view", "default"],
        "Event": ["document_view", "layout_view", "default"],
        "Link": ["document_view", "layout_view", "default"],
        "File": ["document_view", "layout_view", "default"],
        "Image": ["document_view", "layout_view", "default"],
    },
    "workflows_content": {
        "guillotina.interfaces.IResource": "guillotina_basic",
        "guillotina_volto.content.site.ISite": "guillotina_basic",
        "guillotina_volto.content.document.IDocument": "guillotina_basic",
        "guillotina_volto.content.image.IImage": "guillotina_basic",
        "guillotina_volto.content.folder.IFolder": "guillotina_basic",
    },
    "default_blocks": {
        "Document": {
            "blocks": {"tile1": {"@type": "title"}, "tile2": {"@type": "text"}},
            "blocks_layout": {"items": ["tile1", "tile2"]},
        },
        "Site": {
            "blocks_layout": {
                "items": [
                    "cdf077c5-8759-4afb-b7a5-07f45c665ad8",
                    "12821552-d26f-48eb-a1fd-790edb942c30"
                ]
            },
            "blocks": {
                "cdf077c5-8759-4afb-b7a5-07f45c665ad8": {
                    "@type": "title"
                },
                "12821552-d26f-48eb-a1fd-790edb942c30": {
                    "@type": "text",
                    "text": {
                        "blocks": [
                            {
                                "key": "7tq64",
                                "text": "This is Volto running on Guillotina 6",
                                "type": "unstyled",
                                "depth": 0,
                                "inlineStyleRanges": [],
                                "entityRanges": [],
                                "data": {}
                            }
                        ],
                        "entityMap": {}
                    }
                }
            }
        },
    },
    "global_disallowed_types": [
        "User",
        "UserManager",
        "Group",
        "GroupManager",
        "Item",
        "Container",
        "Folder",
    ],
    "default_allow_discussion": False,
    "allow_discussion_types": [],
    "store_json": True,
}

path = "/".join(__file__.split("/")[:-1])

for workflow_file in glob.glob(path + "/workflows/*.yaml"):
    with open(workflow_file, "r") as f:
        workflow_content = yaml.load(f, Loader=yaml.FullLoader)
    ident = workflow_file.split("/")[-1].rstrip(".yaml")
    app_settings["workflows"][ident] = workflow_content


def includeme(root, settings):
    configure.scan("guillotina_volto.interfaces")
    configure.scan("guillotina_volto.api")
    configure.scan("guillotina_volto.behaviors")
    configure.scan("guillotina_volto.content")
    configure.scan("guillotina_volto.fields")
    configure.scan("guillotina_volto.json")
    configure.scan("guillotina_volto.vocabularies")
    configure.scan("guillotina_volto.permissions")
    configure.scan("guillotina_volto.install")
    configure.scan("guillotina_volto.subscribers")
    configure.scan("guillotina_volto.blocks")

    if "guillotina_elasticsearch" in settings.get("applications", []):
        if "load_utilities" not in settings:
            settings["load_utilities"] = {}
        from guillotina.contrib.catalog.pg import app_settings as pg_app_settings

        settings["load_utilities"]["pg_catalog"] = {
            **pg_app_settings["load_utilities"]["catalog"],
            **{"name": "pg_catalog"},
        }
