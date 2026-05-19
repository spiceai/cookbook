FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg2 \
 && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
 && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pyarrow==20.0.0 \
    pyodbc==5.2.0

RUN mkdir -p /data/tpch_sf1

RUN curl -fL https://public-data.spiceai.org/tpch_sf1/region/region.parquet      -o /data/tpch_sf1/region.parquet \
 && curl -fL https://public-data.spiceai.org/tpch_sf1/nation/nation.parquet      -o /data/tpch_sf1/nation.parquet \
 && curl -fL https://public-data.spiceai.org/tpch_sf1/part/part.parquet          -o /data/tpch_sf1/part.parquet \
 && curl -fL https://public-data.spiceai.org/tpch_sf1/supplier/supplier.parquet  -o /data/tpch_sf1/supplier.parquet \
 && curl -fL https://public-data.spiceai.org/tpch_sf1/customer/customer.parquet  -o /data/tpch_sf1/customer.parquet \
 && curl -fL https://public-data.spiceai.org/tpch_sf1/partsupp/partsupp.parquet  -o /data/tpch_sf1/partsupp.parquet \
 && curl -fL https://public-data.spiceai.org/tpch_sf1/orders/orders.parquet      -o /data/tpch_sf1/orders.parquet \
 && curl -fL https://public-data.spiceai.org/tpch_sf1/lineitem/lineitem.parquet  -o /data/tpch_sf1/lineitem.parquet

WORKDIR /app
COPY load-tpch.py .

CMD ["python", "load-tpch.py"]
