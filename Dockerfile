FROM ubuntu:20.04

RUN apt-get update

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get install -y \
    python3.8 \
    python3-pip \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libpq-dev \
    && pip3 install pipenv

COPY Pipfile* ./

RUN pipenv install --verbose

COPY ./app /app
