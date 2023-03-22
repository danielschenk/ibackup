FROM python:3.10-alpine

COPY requirements.txt .
RUN pip install -U --no-cache-dir pip \
    && STATIC_DEPS=true pip install --no-cache-dir -r requirements.txt

COPY ibackup.py .

ENTRYPOINT [ "./ibackup.py", "--cookie-dir", "/data/cookies" ]
