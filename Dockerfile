FROM docker.io/library/python:3.9.6

WORKDIR /app
COPY . /app
RUN pip install -r /app/requirements.txt

#CMD /bin/ash
CMD uwsgi \
  --http-socket 0.0.0.0:5000 \
  --wsgi-file /app/hash_house/app.py \
  --callable app \
  --processes 4 \
  --threads 2
