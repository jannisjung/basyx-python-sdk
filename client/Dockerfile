FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /basyx_client

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN python -m pip install -e .

# Spawn a fake process to keep dev container alive:
# * `tail` usually shows the last lines, of a file
# * `-f` = "follow" -> tail waits for new lines
# * The file `/dev/null` always exists, and anything written to it disappears immediately
CMD ["tail", "-f", "/dev/null"]
