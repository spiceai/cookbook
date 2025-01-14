#!/bin/bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

#!/bin/bash

mkdir -p /home/spark/warehouse
chmod -R 777 /home/spark/warehouse
mkdir -p /home/spark/metastore
chmod -R 777 /home/spark/metastore

# Remove existing metastore_db directory if it exists
if [ -d "/home/spark/metastore/metastore_db" ]; then
    rm -rf /home/spark/metastore/metastore_db
fi

# Start Spark services
start-master.sh -p 7077
sleep 5  # Give master time to start

start-worker.sh spark://spark:7077
sleep 15  # Give worker time to start

# Start Spark Connect server first
$SPARK_HOME/bin/spark-submit \
    --master spark://spark:7077 \
    --class org.apache.spark.sql.connect.service.SparkConnectServer \
    --packages org.apache.spark:spark-connect_2.12:${SPARK_VERSION} \
    --conf "spark.sql.catalogImplementation=hive" \
    --conf "spark.sql.warehouse.dir=/home/spark/warehouse" \
    --conf "spark.hadoop.javax.jdo.option.ConnectionURL=jdbc:derby:;databaseName=/home/spark/metastore/metastore_db;create=true" \
    --conf "spark.hadoop.javax.jdo.option.ConnectionDriverName=org.apache.derby.jdbc.EmbeddedDriver" \
    --name "Spark Connect Server" &

sleep 5  # Wait for Spark Connect to start

# Run the NYC data loading script using spark-submit
if [ -f "/root/.ipython/profile_default/startup/01-load-nyc.py" ]; then
    $SPARK_HOME/bin/spark-submit \
        --master spark://spark:7077 \
        "/root/.ipython/profile_default/startup/01-load-nyc.py"
fi

sleep 5

echo "Spark services started! ✅"

exec "$@"
