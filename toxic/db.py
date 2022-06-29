from __future__ import annotations

from typing import Iterator, Any

import asyncpg


class Database:
    def __init__(self, conn_async: asyncpg.Connection):
        self.conn_async = conn_async

    @staticmethod
    async def connect(host: str, port: int, database: str, user: str, password: str) -> Database:
        conn_async = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        return Database(conn_async)

    async def exec_async(self, query, vars=None):
        if vars is None:
            await self.conn_async.execute(query)
            return

        await self.conn_async.execute(query, *vars)

    async def query_async(self, query, vars=None) -> Iterator:
        if vars is None:
            return await self.conn_async.fetch(query)

        return await self.conn_async.fetch(query, *vars)

    async def query_row_async(self, query, vars=None) -> Any | None:
        if vars is None:
            return await self.conn_async.fetchrow(query)

        return await self.conn_async.fetchrow(query, *vars)
