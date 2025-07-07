FROM ubuntu:latest

RUN apt-get update && apt-get install -y curl

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Symlink uv to /usr/local/bin
RUN ln -s /root/.local/bin/uv /usr/local/bin/uv

RUN mkdir -p /home/iceberg/data/tpch_sf1/customer \
 && mkdir -p /home/iceberg/data/tpch_sf1/lineitem \
 && mkdir -p /home/iceberg/data/tpch_sf1/orders \
 && mkdir -p /home/iceberg/data/tpch_sf1/part \
 && mkdir -p /home/iceberg/data/tpch_sf1/partsupp \
 && mkdir -p /home/iceberg/data/tpch_sf1/supplier \
 && mkdir -p /home/iceberg/data/tpch_sf1/nation \
 && mkdir -p /home/iceberg/data/tpch_sf1/region

RUN curl https://public-data.spiceai.org/tpch_sf1/customer/customer.parquet -o /home/iceberg/data/tpch_sf1/customer/customer.parquet \
 && curl https://public-data.spiceai.org/tpch_sf1/lineitem/lineitem.parquet -o /home/iceberg/data/tpch_sf1/lineitem/lineitem.parquet \
 && curl https://public-data.spiceai.org/tpch_sf1/orders/orders.parquet -o /home/iceberg/data/tpch_sf1/orders/orders.parquet \
 && curl https://public-data.spiceai.org/tpch_sf1/part/part.parquet -o /home/iceberg/data/tpch_sf1/part/part.parquet \
 && curl https://public-data.spiceai.org/tpch_sf1/partsupp/partsupp.parquet -o /home/iceberg/data/tpch_sf1/partsupp/partsupp.parquet \
 && curl https://public-data.spiceai.org/tpch_sf1/supplier/supplier.parquet -o /home/iceberg/data/tpch_sf1/supplier/supplier.parquet \
 && curl https://public-data.spiceai.org/tpch_sf1/nation/nation.parquet -o /home/iceberg/data/tpch_sf1/nation/nation.parquet \
 && curl https://public-data.spiceai.org/tpch_sf1/region/region.parquet -o /home/iceberg/data/tpch_sf1/region/region.parquet

WORKDIR /home/iceberg

COPY pyproject.toml .
COPY uv.lock .
COPY create-tpch-tables.py .
COPY entrypoint.sh .

RUN uv sync

ENTRYPOINT ["/bin/bash", "-c", "/home/iceberg/entrypoint.sh"]
