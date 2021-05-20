FROM python:alpine

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY ./app.py /app.py
ENTRYPOINT [ "python", "-u", "/app.py" ]
