from toxic.db import Database


class UsersRepository:
    def __init__(self, database: Database):
        self.database = database

    async def is_admin(self, user_id: int) -> bool:
        row = await self.database.query_row('SELECT true FROM users WHERE tg_id=$1 AND admin', (user_id,))
        return row is not None
