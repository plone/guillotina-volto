.. contents::

guillotina_volto
================

WIP: This package is a work in progress to provide CMS Volto compatibility on guillotina

Note: This work is inherited from guillotina_cms effort

Start Engine
------------

There's in place a convenience Makefile that setups all the basic enviroment
required for Guillotina Volto to work::

    make

It will start a build of the docker image for development, will start
the needed backend layers and initialize a container at /db/cms/ with this information::

    main api path: http://localhost:8081/db/cms
    root user: root
    root passwd: root
    admin user: admin
    admin password: admin
    GMI path: http://localhost:8081/db/cms/+manage
    SWAGGER path: http://localhost:8081/db/cms/@docs

By default it starts with a reload watch so changes on python code will be reflected on the service without restarting.

Purge and start Engine
----------------------

If you want to delete the container cms and start again with a clean container you should run::

    make purge

Force rebuild of dependencies (a.k.a former buildout :) )
---------------------------------------------------------

If you want to force a new build with master guillotina and local requirements::

    make build

Start with guillotina core development
--------------------------------------

If you want to start with guillotina source core development also enabled you should have
done a checkout of guillotina repository on a sibling folder to guillotina_volto one and start with::

    make init-local
