FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl gpg \
 && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
 && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list \
    -o /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc-dev \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    duckdb==1.3.0 \
    pyodbc==5.2.0

WORKDIR /app
COPY load-tpch.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "load-tpch.py"]
