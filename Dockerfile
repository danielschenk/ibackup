FROM danielschenk/python-slim-iot:master

COPY requirements.txt .
RUN pip install -U --no-cache-dir pip \
    && pip install --no-cache-dir -r requirements.txt

COPY ibackup.py .

ENTRYPOINT [ "./ibackup.py", "--cookie-dir", "/data/cookies" ]
