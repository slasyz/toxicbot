from typing import AsyncIterator

from toxic.db import Database


class UsersRepository:
    def __init__(self, database: Database):
        self.database = database

    async def is_admin(self, user_id: int) -> bool:
        row = await self.database.query_row('SELECT true FROM users WHERE tg_id=%s AND admin', (user_id,))
        return row is not None

    async def get_admins(self) -> AsyncIterator[int]:
        rows = self.database.query('SELECT tg_id FROM users WHERE admin')
        async for row in rows:
            yield row[0]
