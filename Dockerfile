FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn pydantic

COPY env ./env
COPY agents ./agents
COPY server ./server
COPY training ./training
COPY openenv.yaml .

ENV PYTHONPATH=/app

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
