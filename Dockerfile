FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y


COPY . /app

WORKDIR /app/

RUN pip install -r requirements.txt

RUN adduser --disabled-password --gecos '' app