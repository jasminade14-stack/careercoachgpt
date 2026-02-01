FROM python:3.11-slim

WORKDIR /app

# Vorher:
# haystack-integrations-weaviate \

# Nachher:
RUN pip install --no-cache-dir \
    haystack-ai \
    weaviate-haystack \
    sentence-transformers \
    fastapi \
    uvicorn \
    requests


COPY haystack/app.py /app/app.py
COPY haystack/ingest.py /app/ingest.py
COPY haystack/data /app/data

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
