FROM spark:3.5.6
USER root

WORKDIR /data
RUN apt-get update && apt-get install wget unzip curl -y
COPY ./setup_spark.sh /usr/local/bin/setup_spark.sh
RUN chmod +x /usr/local/bin/setup_spark.sh
RUN /usr/local/bin/setup_spark.sh

COPY ./setup_hadoop.sh /usr/local/bin/setup_hadoop.sh
RUN chmod +x /usr/local/bin/setup_hadoop.sh

ENTRYPOINT ["/bin/bash", "-c", "/usr/local/bin/setup_hadoop.sh"]
