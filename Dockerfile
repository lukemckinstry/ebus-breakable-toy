FROM quay.io/azavea/django:3.2-python3.10-slim

RUN pip3 install --upgrade pip

COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY . /usr/src
WORKDIR /usr/src

COPY frontend/build /usr/src/static 

EXPOSE 9202

CMD ["-w", "1", \
     "-b", "0.0.0.0:9202", \
     "--reload", \
     "--log-level", "info", \
     "--error-logfile", "-", \
     "--forwarded-allow-ips", "*", \
     "-k", "gevent", \
     "ebusserver.wsgi"]