from __future__ import annotations

from typing import AsyncIterator, Iterator, Any

import asyncpg
import psycopg2


class Database:
    def __init__(self, conn: psycopg2._psycopg.connection, conn_async: asyncpg.Connection):
        self.conn = conn
        self.conn_async = conn_async

    @staticmethod
    async def connect(host: str, port: int, database: str, user: str, password: str) -> Database:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        conn_async = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        return Database(conn, conn_async)

    async def exec(self, query, vars=None):
        with self.conn, self.conn.cursor() as cur:
            cur.execute(query, vars)
            self.conn.commit()

    async def exec_async(self, query, vars=None):
        if vars is None:
            await self.conn_async.execute(query)
            return

        await self.conn_async.execute(query, *vars)

    async def query(self, query, vars=None) -> AsyncIterator:
        with self.conn, self.conn.cursor() as cur:
            cur.execute(query, vars)
            # TODO: возможно, делать коммит и возвращать итератор с записями
            self.conn.commit()

            if cur.description is None:
                return

            for record in cur:
                yield record

    async def query_async(self, query, vars=None) -> Iterator:
        if vars is None:
            return await self.conn_async.fetch(query)

        return await self.conn_async.fetch(query, *vars)

    async def query_row_async(self, query, vars=None) -> Any | None:
        if vars is None:
            return await self.conn_async.fetchrow(query)

        return await self.conn_async.fetchrow(query, *vars)
