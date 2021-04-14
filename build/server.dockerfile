FROM python:3.9.0-slim-buster

WORKDIR /app

ENV FLASK_APP=/app/server/server.py
ENV DB_NAME=sqlite:///db.sqlite

ADD server/requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

RUN touch db.sqlite

ADD server ./server
ADD api ./api

ADD migrations ./migrations

RUN flask db upgrade

EXPOSE 8080

ENTRYPOINT flask run -h 0.0.0.0 -p 8080
