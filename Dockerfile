# syntax=docker/dockerfile:1
FROM python:3.12-slim

ARG UID=10001

ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/home/app/.local/bin:$PATH"

WORKDIR /app
RUN useradd -m -u $UID app

# Install base (and optional dev) deps first for layer cache efficiency
COPY --chown=app:app requirements*.txt* ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy project
COPY --chown=app:app . .
RUN if [ -f pyproject.toml ]; then pip install .; fi

USER app
CMD ["python","main.py"]
