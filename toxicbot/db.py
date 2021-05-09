import psycopg2

conn: psycopg2._psycopg.connection


def connect(host: str, port: int, database: str, user: str, password: str):
    # TODO: do it better
    global conn

    # TODO: do several attempts
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
