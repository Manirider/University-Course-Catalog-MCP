FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data

RUN mkdir -p /app/data

EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src:/app

CMD ["python", "-m", "uvicorn", "university_catalog.main:app", "--host", "0.0.0.0", "--port", "8080"]