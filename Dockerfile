FROM python:3.12-slim

# Static settings first: these never change, so their layers stay cached
ENV PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies before code: this slow layer is only rebuilt when requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Only the app itself: no tests, no dev tools, no Git history
COPY app/ ./app/

# Create an unprivileged user with no home directory and no login shell, then drop to it
RUN useradd --no-create-home --uid 1000 --shell /usr/sbin/nologin appuser
USER appuser

# Build metadata last: it changes on every commit, so it must not invalidate the layers above
ARG GIT_SHA=unknown
ARG BUILD_TIME=unknown
ENV GIT_SHA=${GIT_SHA} \
    BUILD_TIME=${BUILD_TIME}

EXPOSE 8000

CMD ["sh", "-c", "exec gunicorn --no-control-socket --bind 0.0.0.0:${PORT} app.main:app"]