# syntax=docker/dockerfile:1

FROM python:3.10-slim as base


ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

    COPY requirements.txt .

    RUN apt-get update && \
        apt-get install -y build-essential && \
        python -m pip install --upgrade pip && \
        python -m pip install -r requirements.txt
    


USER appuser

COPY . .

EXPOSE 7860

CMD ["python", "main.py"]
