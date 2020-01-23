FROM ubuntu:19.04

RUN apt-get update && apt-get install -y gnupg2 curl

ARG CURRENT_ENV=${CURRENT_ENV}
ARG UNIT_VERSION=1.9.0-1~disco

COPY ./conf_files/nginx_unit/unit.list /etc/apt/sources.list.d/

RUN curl -fsSL https://nginx.org/keys/nginx_signing.key | apt-key add - && \
    apt-get -y install --reinstall ca-certificates && apt-get -y update && \
    apt-get -y install git unit=$UNIT_VERSION unit-python3.7=$UNIT_VERSION \
                       python3-pip python3-venv

RUN ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip && \
    ln -s /root/.poetry/bin/poetry /usr/bin/poetry && \
    curl https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py --output ./get-poetry.py && \
    python3 ./get-poetry.py --version 0.12.17 && \
    poetry config settings.virtualenvs.create false && \
    rm ./get-poetry.py

COPY pyproject.toml poetry.lock /opt/app/
WORKDIR /opt/app/
RUN /bin/bash -c 'poetry install $(test "$CURRENT_ENV" == prod && echo "--no-dev") --no-interaction --no-ansi'

COPY . /opt/app/
COPY ./conf_files/nginx_unit/conf.json /var/lib/unit/