import json
import pytest
import os

pytestmark = pytest.mark.asyncio


NOT_POSTGRES = os.environ.get("DATABASE", "DUMMY") in ("cockroachdb", "DUMMY")
PG_CATALOG_SETTINGS = {
    "applications": ["guillotina.contrib.catalog.pg"],
    "load_utilities": {
        "catalog": {
            "provides": "guillotina.interfaces.ICatalogUtility",
            "factory": "guillotina.contrib.catalog.pg.utility.PGSearchUtility",
        }
    },
}


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_sharing_tab_assign_permissions(cms_requester):
    async with cms_requester as requester:
        resp, status = await requester(
            "POST",
            "/db/guillotina/users",
            data=json.dumps(
                {
                    "@type": "User",
                    "name": "John Doe 1",
                    "id": "john_doe_1",
                    "username": "john_doe_1",
                    "user_roles": ["guillotina.Member"],
                    "email": "john_doe_1@foo.com",
                    "password": "john_doe_1",
                }
            ),
        )
        assert status == 201

        resp, status = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps({"@type": "CMSFolder", "id": "folder1"}),
        )

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/@sharing"
        )

        # There are no local roles assigned for any user in this context
        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 0

        # Assign local roles to the user
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1/@sharing",
            data=json.dumps(
                {
                    "entries": [
                        {
                            'id': 'john_doe_1',
                            'roles': {
                                'guillotina.Reader': True,
                                'guillotina.Editor': True,
                            },
                        }
                    ],
                }
            ),
        )
        assert status == 200

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/@sharing"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 1

        # Even that the "Editor" role was assigned locally, the global setting has more precedence
        for entry in resp['entries']:
            userid = entry.get('id')
            if userid == 'john_doe_1':
                assert entry['roles']['guillotina.Editor'] is True
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] is True
                assert entry['roles']['guillotina.Reviewer'] is False


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_sharing_tab_inherit_permissions(cms_requester):
    async with cms_requester as requester:
        resp, status = await requester(
            "POST",
            "/db/guillotina/users",
            data=json.dumps(
                {
                    "@type": "User",
                    "name": "John Doe 1",
                    "id": "john_doe_1",
                    "username": "john_doe_1",
                    "user_roles": ["guillotina.Member"],
                    "email": "john_doe_1@foo.com",
                    "password": "john_doe_1",
                }
            ),
        )
        assert status == 201

        resp, status = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps({"@type": "CMSFolder", "id": "folder1"}),
        )
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1",
            data=json.dumps({"@type": "CMSFolder", "id": "folder2"}),
        )

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/folder2/@sharing"
        )

        # There are no local roles assigned nor inherited for any user in this context
        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert resp["inherit"] == True
        assert len(resp["entries"]) == 0

        # Assign local roles to user in parent content
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1/@sharing",
            data=json.dumps(
                {
                    "entries": [
                        {
                            'id': 'john_doe_1',
                            'roles': {
                                'guillotina.Reader': True,
                                'guillotina.Editor': True,
                            },
                        }
                    ],
                }
            ),
        )
        assert status == 200

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/folder2/@sharing"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert resp["inherit"] == True
        assert len(resp["entries"]) == 1

        # In a children folder, roles are acquired
        for entry in resp['entries']:
            userid = entry.get('id')
            if userid == 'john_doe_1':
                assert entry['roles']['guillotina.Editor'] == 'acquired'
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] == 'acquired'
                assert entry['roles']['guillotina.Reviewer'] is False

        # Disable inheritance in subfolder
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1/folder2/@sharing",
            data=json.dumps(
                {
                    "entries": [],
                    "inherit": False
                }
            ),
        )
        assert status == 200

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/folder2/@sharing"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert resp["inherit"] == False
        assert len(resp["entries"]) == 0

        # Assign local roles to subfolder
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1/folder2/@sharing",
            data=json.dumps(
                {
                    "entries": [
                        {
                            'id': 'john_doe_1',
                            'roles': {
                                'guillotina.Reader': True,
                                'guillotina.Reviewer': True,
                            },
                        }
                    ],
                }
            ),
        )
        assert status == 200

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/folder2/@sharing"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert resp["inherit"] == False
        assert len(resp["entries"]) == 1

        for entry in resp['entries']:
            userid = entry.get('id')
            if userid == 'john_doe_1':
                assert entry['roles']['guillotina.Editor'] is False
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] is True
                assert entry['roles']['guillotina.Reviewer'] is True

        # Enable back inheritance in subfolder
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1/folder2/@sharing",
            data=json.dumps(
                {
                    "entries": [],
                    "inherit": True
                }
            ),
        )
        assert status == 200

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/folder2/@sharing"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert resp["inherit"] == True
        assert len(resp["entries"]) == 1

        # Acquired roles have more precedence over locally assigned
        for entry in resp['entries']:
            userid = entry.get('id')
            if userid == 'john_doe_1':
                assert entry['roles']['guillotina.Editor'] == 'acquired'
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] == 'acquired'
                assert entry['roles']['guillotina.Reviewer'] is True

        # Disable inheritance in subfolder
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1/folder2/@sharing",
            data=json.dumps(
                {
                    "entries": [],
                    "inherit": False
                }
            ),
        )
        assert status == 200

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/folder2/@sharing"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert resp["inherit"] == False
        assert len(resp["entries"]) == 1

        # No acquired roles, only assigned ones
        for entry in resp['entries']:
            userid = entry.get('id')
            if userid == 'john_doe_1':
                assert entry['roles']['guillotina.Editor'] is False
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] is True
                assert entry['roles']['guillotina.Reviewer'] is True


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_sharing_tab_search(cms_requester):
    async with cms_requester as requester:
        users = [
            ("John Doe 1", "john_doe_1"),
            ("John Doe 2", "john_doe_2"),
            ("John Doe 3", "john_doe_3"),
        ]

        for name, userid in users:
            user_roles = ["guillotina.Member"]
            resp, status = await requester(
                "POST",
                "/db/guillotina/users",
                data=json.dumps(
                    {
                        "@type": "User",
                        "name": name,
                        "id": userid,
                        "username": userid,
                        "user_roles": user_roles,
                        "email": f"{userid}@foo.com",
                        "password": userid,
                    }
                ),
            )
            assert status == 201

        groups = [
            ("Doe Users", "doe_users"),
            ("Another Group", "another_group"),
        ]

        for name, groupid in groups:
            user_roles = ["guillotina.Member"]
            resp, status = await requester(
                "POST",
                "/db/guillotina/groups",
                data=json.dumps(
                    {
                        "@type": "Group",
                        "groupname": name,
                        "id": groupid,
                        "user_roles": user_roles,
                    }
                ),
            )
            assert status == 201

        resp, status = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps({"@type": "CMSFolder", "id": "folder1"}),
        )

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/@sharing"
        )

        # There are no local roles assigned for any user in this context
        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 0

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/@sharing?search=john"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 3

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/@sharing?search=doe"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 4


        resp, status = await requester(
            "GET", "/db/guillotina/folder1/@sharing?search=another"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 1


@pytest.mark.app_settings(PG_CATALOG_SETTINGS)
@pytest.mark.skipif(NOT_POSTGRES, reason="Only PG")
async def test_sharing_tab_global_permissions(cms_requester):
    async with cms_requester as requester:
        users = [
            ("John Doe 1", "john_doe_1"),
            ("John Doe 2", "john_doe_2"),
            ("John Doe 3", "john_doe_3"),
        ]

        for name, userid in users:
            user_roles = ["guillotina.Member"]
            if userid == "john_doe_1":
                user_roles = [
                    "guillotina.Editor",
                    "guillotina.Member"
                ]
            resp, status = await requester(
                "POST",
                "/db/guillotina/users",
                data=json.dumps(
                    {
                        "@type": "User",
                        "name": name,
                        "id": userid,
                        "username": userid,
                        "user_roles": user_roles,
                        "email": f"{userid}@foo.com",
                        "password": userid,
                    }
                ),
            )
            assert status == 201

        resp, status = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps({"@type": "CMSFolder", "id": "folder1"}),
        )
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1",
            data=json.dumps({"@type": "CMSFolder", "id": "folder2"}),
        )

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/@sharing"
        )

        # There are no local roles assigned for any user in this context
        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 0

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/@sharing?search=john"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 3

        # Search results, john_doe_1 has 1 global role
        for entry in resp['entries']:
            userid = entry.get('id')
            if userid == 'john_doe_1':
                assert entry['roles']['guillotina.Editor'] == 'global'
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] is False
                assert entry['roles']['guillotina.Reviewer'] is False
            if userid == 'john_doe_2':
                assert entry['roles']['guillotina.Editor'] is False
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] is False
                assert entry['roles']['guillotina.Reviewer'] is False
            if userid == 'john_doe_3':
                assert entry['roles']['guillotina.Editor'] is False
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] is False
                assert entry['roles']['guillotina.Reviewer'] is False

        # Assign local roles to 2 users
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1/@sharing",
            data=json.dumps(
                {
                    "entries": [
                        {
                            'id': 'john_doe_1',
                            'roles': {
                                'guillotina.Reader': True,
                                'guillotina.Editor': True,
                            },
                        },
                        {
                            'id': 'john_doe_2',
                            'roles': {
                                'guillotina.Reader': True,
                                'guillotina.Editor': True,
                            },
                        }
                    ],
                }
            ),
        )
        assert status == 200

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/@sharing"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 2

        # Even that the "Editor" role was assigned locally, the global setting has more precedence
        for entry in resp['entries']:
            userid = entry.get('id')
            if userid == 'john_doe_1':
                assert entry['roles']['guillotina.Editor'] == 'global'
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] is True
                assert entry['roles']['guillotina.Reviewer'] is False
            if userid == 'john_doe_2':
                assert entry['roles']['guillotina.Editor'] is True
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] is True
                assert entry['roles']['guillotina.Reviewer'] is False

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/folder2/@sharing"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 2

        # In a children folder, roles are acquired
        for entry in resp['entries']:
            userid = entry.get('id')
            if userid == 'john_doe_1':
                assert entry['roles']['guillotina.Editor'] == 'global'
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] == 'acquired'
                assert entry['roles']['guillotina.Reviewer'] is False
            if userid == 'john_doe_2':
                assert entry['roles']['guillotina.Editor'] == 'acquired'
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] == 'acquired'
                assert entry['roles']['guillotina.Reviewer'] is False

        # Assign local roles to subfolder
        resp, status = await requester(
            "POST",
            "/db/guillotina/folder1/folder2/@sharing",
            data=json.dumps(
                {
                    "entries": [
                        {
                            'id': 'john_doe_1',
                            'roles': {
                                'guillotina.Reader': True,
                                'guillotina.Editor': True,
                                'guillotina.Reviewer': True,
                            },
                        }
                    ],
                }
            ),
        )
        assert status == 200

        resp, status = await requester(
            "GET", "/db/guillotina/folder1/folder2/@sharing"
        )

        assert 'available_roles' in resp
        assert 'entries' in resp
        assert 'inherit' in resp
        assert len(resp["entries"]) == 2

        # Acquired and Global roles have more precedence over locally assigned
        for entry in resp['entries']:
            userid = entry.get('id')
            if userid == 'john_doe_1':
                assert entry['roles']['guillotina.Editor'] == 'global'
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] == 'acquired'
                assert entry['roles']['guillotina.Reviewer'] is True
            if userid == 'john_doe_2':
                assert entry['roles']['guillotina.Editor'] == 'acquired'
                assert entry['roles']['guillotina.Owner'] is False
                assert entry['roles']['guillotina.Reader'] == 'acquired'
                assert entry['roles']['guillotina.Reviewer'] is False
