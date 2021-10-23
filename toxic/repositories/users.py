from collections.abc import Iterator

from toxic.db import Database


class UsersRepository:
    def __init__(self, database: Database):
        self.database = database

    def is_admin(self, user_id: int) -> bool:
        row = self.database.query_row('SELECT true FROM users WHERE tg_id=%s AND admin', (user_id,))
        return row is not None

    def get_admins(self) -> Iterator[int]:
        rows = self.database.query('SELECT tg_id FROM users WHERE admin')
        for row in rows:
            yield row[0]
