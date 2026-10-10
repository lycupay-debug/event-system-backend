FROM python:3.14.8-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install Node.js 22 and the official lark-cli in this image only.
# This does not install Node.js on the Ubuntu host or modify the n8n container.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install --global @larksuite/cli@latest \
    && node --version \
    && npm --version \
    && lark-cli --help >/dev/null \
    && apt-get purge -y --auto-remove curl gnupg \
    && rm -rf /var/lib/apt/lists/* /root/.npm

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/requirements.txt

COPY app/ /app/app/
COPY test/ /app/test/

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER 10001:10001

CMD ["python", "-m", "app.main"]
