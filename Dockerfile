FROM python:3.6.2

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install Dockerize
ENV DOCKERIZE_VERSION v0.6.0

# install environment dependencies
RUN apt-get update -yqq \
  && apt-get install -yqq --no-install-recommends \
    openssl \
  && apt-get -q clean

RUN  wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
 && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
 && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

ADD ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

RUN mkdir -p /data
ENV SAVE_PATH /data

ADD jholiday.py /usr/src/app

ADD brands /usr/src/app/brands
ADD main.py /usr/src/app

CMD [ "python", "-u", "./main.py" ]