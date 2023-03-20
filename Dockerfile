FROM python:3.10-alpine

RUN apk update && apk add --no-cache \
    py-cryptography

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ibackup.py .

ENTRYPOINT [ "./ibackup.py", "--cookie-dir", "/data/cookies" ]
