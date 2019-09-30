#!/bin/bash
function cassandra_ready() {
    count=0
    while ! cqlsh -e "describe cluster;" 2>&1 ; do
        echo "waiting for cassandra"
        if [ $count -gt 30 ]
        then
            exit
        fi
        (( count += 1 ))
        sleep 1
    done
    echo "cassandra is ready"
}

cassandra_ready
cqlsh -e "create keyspace key1 with replication = {'class': 'SimpleStrategy', 'replication_factor': 3}; USE key1; CREATE TABLE IF NOT EXISTS user (username text PRIMARY KEY, password text, id uuid);CREATE TABLE IF NOT EXISTS session (id uuid PRIMARY KEY, username text);"