# fake_sms

`fake_sms` is a Django-based OTP testing service. It stores one pending OTP per mobile number in Redis, allows verification through a simple API, and exposes a browser portal for looking up the current OTP during development.

This project is intended for internal and development use only. It should not be exposed publicly.

## What It Does

- Stores OTP tokens by mobile number.
- Verifies OTP tokens and removes them after a successful match.
- Provides a portal UI for searching the current OTP for a mobile number.
- Runs with Django, Django REST Framework, Redis, and Gunicorn.

## How It Works

The active OTP flow is implemented in `core/services/otp_store.py`.

- `send` stores `{ mobile, otp }` in Redis with a default TTL of 300 seconds.
- `verify` compares the submitted OTP with the cached value.
- A successful verification deletes the cached record immediately.

The database model `OTPRecord` exists in `core/models.py`, but the current API path does not write to that table. In practice, OTP storage and verification are Redis-backed.

## API

The project exposes two unauthenticated API endpoints at the site root:

- `POST /send/`
- `POST /verify/`

Both endpoints accept JSON payloads with the same fields:

```json
{
  "mobile": "09121234567",
  "otp": "123456"
}
```

### `POST /send/`

Stores an OTP for a mobile number.

Request:

```bash
curl -X POST http://localhost:8000/send/ \
  -H "Content-Type: application/json" \
  -d '{"mobile":"09121234567","otp":"123456"}'
```

Response:

```json
{
  "success": true
}
```

### `POST /verify/`

Checks whether the submitted OTP matches the cached value.

Request:

```bash
curl -X POST http://localhost:8000/verify/ \
  -H "Content-Type: application/json" \
  -d '{"mobile":"09121234567","otp":"123456"}'
```

Response on match:

```json
{
  "success": true
}
```

Response on mismatch, missing record, or expired record:

```json
{
  "success": false
}
```

### Rate Limiting

The OTP endpoints are throttled with DRF using Redis-backed counters.

Default limits:

- `otp_send_ip`: `5/min`
- `otp_send_mobile`: `3/min`
- `otp_verify_ip`: `10/min`
- `otp_verify_mobile`: `5/min`

Behavior:

- Each endpoint is limited independently.
- Requests are throttled both by client IP and by mobile number.
- Successful OTP verification still deletes the OTP as before.
- When the limit is exceeded, the API returns HTTP `429 Too Many Requests`.

These limits can be changed with environment variables:

- `OTP_SEND_IP_RATE`
- `OTP_SEND_MOBILE_RATE`
- `OTP_VERIFY_IP_RATE`
- `OTP_VERIFY_MOBILE_RATE`

## Portal

The browser portal is mounted at:

- `GET /portal/`

It lets an operator search by mobile number and view the pending OTP if it exists in Redis.

The portal is meant for development and debugging. It is not protected by authentication or authorization.

## Configuration

The project reads configuration from environment variables and `.env`.

Required database setting:

- `DATABASE_URL`

Redis setting:

- `REDIS_URL` - optional, defaults to `redis://redis:6379/0`

Common Django settings:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`

Important defaults from the current settings:

- `DEBUG` defaults to `True`
- `ALLOWED_HOSTS` defaults to `localhost` and `127.0.0.1`
- OTP cache TTL defaults to 300 seconds

Note: the checked-in `.env` file uses `DJANGO_DEBUG` and `DJANGO_ALLOWED_HOSTS`, while `fake_sms/settings.py` currently reads `DEBUG` and `ALLOWED_HOSTS`. The app still starts because the settings file has defaults, but those two `.env` values are not currently consumed unless the settings file is updated.

## Local Development

### Prerequisites

- Python 3.14+
- Redis
- A database reachable through `DATABASE_URL`

### Install dependencies

Using `uv`:

```bash
uv sync
```

Using `pip`:

```bash
pip install -r requirements.txt
```

### Run migrations

```bash
python manage.py migrate
```

### Start the development server

```bash
python manage.py runserver
```

The app will be available at:

- `http://127.0.0.1:8000/portal/`
- `http://127.0.0.1:8000/send/`
- `http://127.0.0.1:8000/verify/`

## Docker

The `Dockerfile` builds a Python 3.14 slim image, installs project dependencies, and starts Gunicorn on port `8000`.

Build the image:

```bash
docker build -t fake_sms .
```

Run the container:

```bash
docker run --rm -p 8000:8000 --env-file .env fake_sms
```

## Docker Compose

The provided `docker-compose.yml` starts two services:

- `redis`
- `web`

The `web` service:

- waits for Redis to become healthy
- runs migrations
- collects static files
- starts Gunicorn

Start the stack with:

```bash
docker compose up --build
```

## Project Layout

```text
fake_sms/
├── core/
│   ├── api/
│   ├── migrations/
│   ├── services/
│   ├── models.py
│   └── views.py
├── portal/
│   ├── templates/
│   ├── urls.py
│   └── views.py
├── fake_sms/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── README.md
```

## Important Notes

- OTP verification is destructive: a successful verify removes the cached OTP.
- The current API has no authentication, rate limiting, or CSRF protection because the DRF views explicitly disable authentication and permissions.
- The portal and API are intended for development and internal testing, not production SMS handling.
- `OTPRecord` exists in the database schema, but the service currently uses Redis as the source of truth for live OTPs.

## License

See [LICENSE](LICENSE).
