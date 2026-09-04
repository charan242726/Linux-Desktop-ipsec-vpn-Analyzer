FROM python:3.11-slim

WORKDIR /app

# tshark is needed at runtime by pyshark (extract_ike_features.py)
RUN apt-get update && apt-get install -y --no-install-recommends tshark \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ /app/scripts/
COPY api/ /app/api/
COPY models/ /app/models/

WORKDIR /app/api
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
