import requests
from requests.auth import HTTPBasicAuth


auth = HTTPBasicAuth("root", "root")


def initdb():
    groot = "http://localhost:8081/db"

    resp = requests.get(
        groot,
        auth=auth,
    )
    assert resp.status_code == 200

    # Create container
    resp = requests.post(
        f"{groot}/",
        auth=auth,
        json={"@type": "Site", "id": "web", "title": "Guillotina Volto Site"},
    )
    assert resp.status_code in (200, 409)

    # Install CMS package
    resp = requests.post("{}/web/@addons".format(groot), auth=auth, json={"id": "cms"})
    assert resp.status_code in (200, 412)

    # Install DB users package
    resp = requests.post(
        "{}/web/@addons".format(groot), auth=auth, json={"id": "dbusers"}
    )

    assert resp.status_code in (200, 412)

    # Create manager group
    payload = {
        "@type": "Group",
        "id": "managers",
        "user_roles": [
            "guillotina.Manager",
            "guillotina.ContainerAdmin",
            "guillotina.Owner",
        ],
    }
    resp = requests.post("{}/web/groups".format(groot), auth=auth, json=payload)

    assert resp.status_code in (201, 409)

    # Create initial user (admin is reserved word)
    payload = {
        "@type": "User",
        "username": "admin_user",
        "email": "foo@bar.com",
        "password": "admin",
        "user_groups": ["managers"],
    }
    resp = requests.post("{}/web/users".format(groot), auth=auth, json=payload)
    assert resp.status_code in (201, 409)

    resp = requests.get("{}/web".format(groot), auth=auth)
    assert resp.status_code == 200

    if resp.json()["review_state"] == "private":
        resp = requests.post(
            "{}/web/@workflow/publish".format(groot), json={}, auth=auth
        )
        assert resp.status_code in (200, 500, 404)

    resp = requests.get(
        "{}/web/@user".format(groot), auth=HTTPBasicAuth("admin_user", "admin")
    )
    assert "managers" in resp.json()["admin_user"]["groups"]
    resp = requests.get("{}/web/".format(groot))
    assert resp.status_code == 200


def deletedb():
    groot = "http://localhost:8081/db"

    resp = requests.delete("{}/web".format(groot), auth=auth)

    assert resp.status_code == 200
