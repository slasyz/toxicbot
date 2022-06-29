from __future__ import annotations

from typing import Iterator, Any

import asyncpg


class Database:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    @staticmethod
    async def connect(host: str, port: int, database: str, user: str, password: str) -> Database:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        return Database(conn)

    async def exec(self, query, vars=None):
        if vars is None:
            await self.conn.execute(query)
            return

        await self.conn.execute(query, *vars)

    async def query(self, query, vars=None) -> Iterator:
        if vars is None:
            return await self.conn.fetch(query)

        return await self.conn.fetch(query, *vars)

    async def query_row(self, query, vars=None) -> Any | None:
        if vars is None:
            return await self.conn.fetchrow(query)

        return await self.conn.fetchrow(query, *vars)
