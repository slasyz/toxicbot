FROM postgres:13.4-alpine

RUN apk add --no-cache procps
COPY createdb.sql /docker-entrypoint-initdb.d/createdb.sql
