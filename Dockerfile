FROM python:3.10-alpine

COPY requirements.txt .
RUN apk update && apk add --no-cache \
        musl-dev \
        python3-dev \
        libffi-dev \
        openssl-dev \
        cargo \
        pkgconfig \
        && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del \
        musl-dev \
        python3-dev \
        libffi-dev \
        openssl-dev \
        cargo \
        pkgconfig

COPY ibackup.py .

ENTRYPOINT [ "./ibackup.py", "--cookie-dir", "/data/cookies" ]
