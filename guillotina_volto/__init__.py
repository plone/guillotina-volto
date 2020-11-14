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
        "Container": ["document_view", "layout_view"],
        "News": ["document_view", "layout_view"],
        "Event": ["document_view", "layout_view"],
        "Link": ["document_view", "layout_view"],
        "File": ["document_view", "layout_view"],
        "Image": ["document_view", "layout_view"],
    },
    "workflows_content": {
        "guillotina.interfaces.IResource": "private",
        "guillotina.interfaces.IContainer": "basic",
        "guillotina_volto.content.document.IDocument": "basic",
        "guillotina_volto.content.image.IImage": "basic",
        "guillotina_volto.content.folder.IFolder": "basic",
    },
    "default_blocks": {
        "Document": {
            "blocks": {"tile1": {"@type": "title"}, "tile2": {"@type": "text"}},
            "blocks_layout": {"items": ["tile1", "tile2"]},
        },
        "Container": {
            "blocks": {"tile1": {"@type": "title"}, "tile2": {"@type": "text"}},
            "blocks_layout": {"items": ["tile1", "tile2"]},
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
    configure.scan("guillotina_volto.utilities")
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
