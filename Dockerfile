FROM python:3.11-slim AS compile-image

RUN apt-get update && apt-get install --no-install-recommends -y \
    python3-cryptography

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -U --no-cache-dir pip \
    && STATIC_DEPS=true pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

COPY --from=compile-image /opt/venv /opt/venv
COPY ibackup.py .

ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT [ "./ibackup.py", "--cookie-dir", "/data/cookies" ]
