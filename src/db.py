import psycopg2

from src import config

conn: psycopg2._psycopg.connection


def connect():
    global conn

    conn = psycopg2.connect(
        host=config.c['database']['host'],
        database=config.c['database']['database'],
        user=config.c['database']['user'],
        password=config.c['database']['password']
    )
