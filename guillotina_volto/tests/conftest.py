from pytest_docker_fixtures import images


images.configure("cockroach", "cockroachdb/cockroach", "v2.0.5")

images.configure(
    "postgresql",
    version="15.2",
    env={
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_DB": "guillotina",
        "POSTGRES_USER": "postgres",
    },
)


pytest_plugins = [
    "pytest_docker_fixtures",
    "guillotina.tests.fixtures",
    "guillotina_volto.tests.fixtures",
]
