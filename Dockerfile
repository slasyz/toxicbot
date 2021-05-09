FROM python:3.9.5-slim-buster

EXPOSE 8000
EXPOSE 8001

WORKDIR /app

RUN apt-get update -y && apt-get install -y build-essential gcc libpq-dev postgresql-client && apt-get purge --auto-remove && apt-get clean

COPY ./requirements.txt ./Makefile /app/
COPY ./makefiles/Makefile.python /app/makefiles/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN make deps

COPY . /app/

ENTRYPOINT make run
