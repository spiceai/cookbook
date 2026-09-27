FROM python:3.11-slim

RUN pip install --no-cache-dir deltalake==0.25.5 pandas==2.2.3 pyarrow==19.0.1 requests==2.32.3

COPY seed_data.py /seed_data.py

ENTRYPOINT ["python", "/seed_data.py"]
