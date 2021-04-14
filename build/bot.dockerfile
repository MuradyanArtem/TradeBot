FROM python:3.9.0-slim-buster

WORKDIR /app

ADD bot/requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

ADD bot ./bot
ADD api ./api

ENTRYPOINT python3 -m bot
