FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python --version
RUN python -m venv .venv
RUN ls -la .venv/bin/
RUN .venv/bin/pip install --upgrade pip
RUN .venv/bin/pip install -r requirements.txt
RUN .venv/bin/python -c "import django; print('Django OK:', django.__version__)"

COPY . .

RUN .venv/bin/python manage.py collectstatic --noinput

EXPOSE 8000

CMD [".venv/bin/gunicorn", "fake_sms.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1"]