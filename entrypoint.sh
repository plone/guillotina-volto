#!/usr/bin/env bash
set -Ex

CALLING=$@

function init_container {
    echo "Initializing container db/web"
    echo "$CALLING"
    $CALLING 2>&1 &
    G_PID=$!
    while ! nc -z localhost 8081; do   
        sleep 0.1 # wait for 1/10 of the second before check again
    done
    sleep 1
    initdb
    kill $G_PID
    test -n "$START" && exit 0
}

function delete_container {
    echo "Deleting container db/web"
    echo "$CALLING"
    $CALLING 2>&1 &
    G_PID=$!
    while ! nc -z localhost 8081; do   
        sleep 0.1 # wait for 1/10 of the second before check again
    done
    sleep 1
    deletedb
    kill $G_PID
    test -n "$START" && exit 0
}

function local_load {
    ACTUAL_PATH=$PWD
    cd /usr/src/guillotina; python setup.py develop
    cd $ACTUAL_PATH
}


test -n "$LOCAL" && local_load
test -n "$PURGE" && delete_container
test -n "$INIT" && init_container

echo "START GUILLOTINA SERVER"

exec "$@" "--reload"
