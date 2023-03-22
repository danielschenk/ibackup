FROM python:3.10-alpine AS compile-image

RUN apk update && apk add \
    rust

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -U --no-cache-dir pip \
    && STATIC_DEPS=true pip install --no-cache-dir -r requirements.txt

FROM python:3.10-alpine
COPY --from=compile-image /opt/venv .
COPY ibackup.py .

ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT [ "./ibackup.py", "--cookie-dir", "/data/cookies" ]
