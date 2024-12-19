#!/bin/bash

CONTAINER_NAME="superset-sales-bi-demo"

docker exec -it $CONTAINER_NAME superset fab create-admin \
              --username admin \
              --firstname Superset \
              --lastname Admin \
              --email admin@superset.com \
              --password admin

docker exec -it $CONTAINER_NAME superset db upgrade
docker exec -it $CONTAINER_NAME superset init
