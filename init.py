import requests
from requests.auth import HTTPBasicAuth


auth = HTTPBasicAuth("root", "root")

resp = requests.delete(
    "http://localhost:8081/db/volto", auth=auth
)
print(resp)


resp = requests.post(
    "http://localhost:8081/db/", json={"@type": "Site", "id": "volto"}, auth=auth
)
print(resp)

resp = requests.post(
    "http://localhost:8081/db/volto/@addons", json={"id": "dbusers"}, auth=auth
)
print(resp)

resp = requests.post("http://localhost:8081/db/volto/@addons", json={"id": "cms"}, auth=auth)
print(resp)

resp = requests.post(
    "http://localhost:8081/db/volto/groups",
    json={
        "@type": "Group",
        "id": "Managers",
        "user_roles": ["guillotina.Manager", "guillotina.ContainerAdmin", "guillotina.Owner"],
    },
    auth=auth,
)
print(resp)

resp = requests.post(
    "http://localhost:8081/db/volto/users",
    json={
        "@type": "User",
        "username": "admin",
        "email": "foo@bar.com",
        "password": "admin",
        "groups": ["Managers"]
    },
    auth=auth,
)
print(resp)


resp = requests.post("http://localhost:8081/db/volto/@workflow/retire", json={}, auth=auth)
resp = requests.post("http://localhost:8081/db/volto/@workflow/publish", json={}, auth=auth)
print(resp)
