from __future__ import annotations

from typing import Iterator, Any

import asyncpg


class Database:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    @staticmethod
    async def connect(host: str, port: int, database: str, user: str, password: str) -> Database:
        pool = await asyncpg.create_pool(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,

            min_size=2,
            max_size=10,
        )

        return Database(pool)

    async def exec(self, query, vars=None):
        if vars is None:
            await self.pool.execute(query)
            return

        await self.pool.execute(query, *vars)

    async def query(self, query, vars=None) -> Iterator:
        if vars is None:
            return await self.pool.fetch(query)

        return await self.pool.fetch(query, *vars)

    async def query_row(self, query, vars=None) -> Any | None:
        if vars is None:
            return await self.pool.fetchrow(query)

        return await self.pool.fetchrow(query, *vars)
