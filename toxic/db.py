from __future__ import annotations

from typing import Iterator

import psycopg2


class Database:
    def __init__(self, conn: psycopg2._psycopg.connection):
        self.conn = conn

    @staticmethod
    async def connect(host: str, port: int, database: str, user: str, password: str) -> Database:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        return Database(conn)

    def exec(self, query, vars=None):
        with self.conn, self.conn.cursor() as cur:
            cur.execute(query, vars)
            self.conn.commit()

    def query(self, query, vars=None) -> Iterator:
        with self.conn, self.conn.cursor() as cur:
            cur.execute(query, vars)
            # TODO: возможно, делать коммит и возвращать итератор с записями
            self.conn.commit()

            if cur.description is None:
                return

            for record in cur:
                yield record

    def query_row(self, query, vars=None):
        for record in self.query(query, vars):
            return record

        return None
