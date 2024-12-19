#!/bin/bash

CONTAINER_NAME="superset-sales-bi-demo"

docker exec -it $CONTAINER_NAME superset import-dashboards \
              --path /dashboard/dashboard-sales-demo.zip \
              --username admin