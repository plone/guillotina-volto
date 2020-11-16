# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

all: init start

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build:
	docker-compose build guillotina

init: start-dependencies
	docker-compose run -e INIT=True -e START=False --service-ports guillotina guillotina -c config-dockercompose.yaml

start: start-dependencies
	docker-compose run --service-ports guillotina guillotina -c config-dockercompose.yaml

purge: start-dependencies ## Deletes and resets the DB
	docker-compose run -e INIT=True -e PURGE=True -e START=False --service-ports guillotina guillotina -c config-dockercompose.yaml

start-local: start-dependencies
	docker-compose run -e LOCAL=True --service-ports guillotina-local guillotina -c config-dockercompose.yaml

start-backend: ## Starts Guillotina
	guillotina -c config.yaml

start-dependencies: ## Starts dependencies (PG, ES, Redis)
	docker-compose up --no-start postgres
	docker-compose start postgres

stop-dependencies: ## Starts dependencies (PG, ES, Redis)
	docker-compose stop postgres

docker:
	docker build -t plone/guillotina_volto:latest .
	docker push plone/guillotina_volto:latest
