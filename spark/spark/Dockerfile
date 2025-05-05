# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# syntax=docker/dockerfile:1
FROM python:3.10-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      sudo \
      curl \
      vim \
      unzip \
      openjdk-11-jdk \
      build-essential \
      software-properties-common \
      ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Jupyter and other python deps
COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENV SPARK_HOME=${SPARK_HOME:-"/opt/spark"}
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH

WORKDIR ${SPARK_HOME}

ENV SPARK_VERSION=3.5.5

RUN mkdir -p /home/spark/data \
    /home/spark/notebooks \
    /root/.ipython/profile_default/startup

RUN mkdir -p /home/spark/warehouse && chmod -R 777 /home/spark/warehouse
RUN mkdir -p /home/spark/metastore && chmod -R 777 /home/spark/metastore

COPY ipython/startup/*.py /root/.ipython/profile_default/startup/

# Download spark
RUN cd ${SPARK_HOME} \
    && curl https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz -o spark-${SPARK_VERSION}-bin-hadoop3.tgz \
    && tar xvzf spark-${SPARK_VERSION}-bin-hadoop3.tgz --directory /opt/spark --strip-components 1 \
    && rm -rf spark-${SPARK_VERSION}-bin-hadoop3.tgz

ENV SPARK_VERSION=3.5.5
RUN cd ${SPARK_HOME} && \
    wget https://repo1.maven.org/maven2/org/apache/spark/spark-connect_2.12/${SPARK_VERSION}/spark-connect_2.12-${SPARK_VERSION}.jar -P jars/ && \
    wget https://repo1.maven.org/maven2/org/apache/spark/spark-connect-client-jvm_2.12/${SPARK_VERSION}/spark-connect-client-jvm_2.12-${SPARK_VERSION}.jar -P jars/ && \
    wget https://repo1.maven.org/maven2/io/grpc/grpc-all/1.47.0/grpc-all-1.47.0.jar -P jars/ && \
    wget https://repo1.maven.org/maven2/io/grpc/grpc-netty/1.47.0/grpc-netty-1.47.0.jar -P jars/ && \
    wget https://repo1.maven.org/maven2/io/netty/netty-codec-http2/4.1.77.Final/netty-codec-http2-4.1.77.Final.jar -P jars/ && \
    wget https://repo1.maven.org/maven2/io/netty/netty-handler-proxy/4.1.77.Final/netty-handler-proxy-4.1.77.Final.jar -P jars/

RUN mkdir -p /home/spark/data \
    && curl https://data.cityofnewyork.us/resource/tg4x-b46p.json > /home/spark/data/nyc_film_permits.json \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-04.parquet -o /home/spark/data/yellow_tripdata_2022-04.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-03.parquet -o /home/spark/data/yellow_tripdata_2022-03.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-02.parquet -o /home/spark/data/yellow_tripdata_2022-02.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-01.parquet -o /home/spark/data/yellow_tripdata_2022-01.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-12.parquet -o /home/spark/data/yellow_tripdata_2021-12.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-11.parquet -o /home/spark/data/yellow_tripdata_2021-11.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-10.parquet -o /home/spark/data/yellow_tripdata_2021-10.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-09.parquet -o /home/spark/data/yellow_tripdata_2021-09.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-08.parquet -o /home/spark/data/yellow_tripdata_2021-08.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-07.parquet -o /home/spark/data/yellow_tripdata_2021-07.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-06.parquet -o /home/spark/data/yellow_tripdata_2021-06.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-05.parquet -o /home/spark/data/yellow_tripdata_2021-05.parquet \
    && curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-04.parquet -o /home/spark/data/yellow_tripdata_2021-04.parquet

# Add a notebook command
RUN echo '#! /bin/sh' >> /bin/notebook \
    && echo 'export PYSPARK_DRIVER_PYTHON=jupyter-notebook' >> /bin/notebook \
    && echo "export PYSPARK_DRIVER_PYTHON_OPTS=\"--notebook-dir=/home/spark/notebooks --ip='*' --NotebookApp.token='' --NotebookApp.password='' --port=8888 --no-browser --allow-root\"" >> /bin/notebook \
    && echo "pyspark" >> /bin/notebook \
    && chmod u+x /bin/notebook

COPY spark-defaults.conf /opt/spark/conf
ENV PATH="/opt/spark/sbin:/opt/spark/bin:${PATH}"

RUN chmod u+x /opt/spark/sbin/* && \
    chmod u+x /opt/spark/bin/*

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["notebook"]
