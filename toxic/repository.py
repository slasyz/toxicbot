import json
from typing import AsyncIterator

from toxic.db import Database


class Repository:
    def __init__(self, database: Database):
        self.database = database

    async def is_admin(self, user_id: int) -> bool:
        row = await self.database.query_row('SELECT true FROM users WHERE tg_id=$1 AND admin', (user_id,))
        return row is not None

    async def _set_setting(self, key: str, value: str | None):
        if value is None:
            await self.database.exec('DELETE FROM settings WHERE key=$1', (key,))
            return

        await self.database.exec('''
            INSERT INTO settings(key, value) 
            VALUES($1, $2)
            ON CONFLICT(key) DO UPDATE
                SET value = $3
        ''', (key, value, value))

    async def _get_setting(self, key: str) -> str | None:
        row = await self.database.query_row('SELECT value FROM settings WHERE key=$1', (key,))
        if row is None:
            return None

        return row[0]

    async def spotify_token_get(self) -> dict | None:
        value_str = await self._get_setting('spotify_token')
        if value_str is None:
            return None

        return json.loads(value_str)

    async def spotify_token_set(self, token_info: dict):
        value_str = json.dumps(token_info)
        return await self._set_setting('spotify_token', value_str)

    async def list_chats(self) -> AsyncIterator[tuple[int, str]]:
        rows = await self.database.query('''
                    SELECT c.tg_id, c.title
                    FROM chats c
                    WHERE c.tg_id < 0
                    UNION
                    SELECT u.tg_id, btrim(concat(u.first_name, ' ', u.last_name))
                    FROM users u
                ''')
        for row in rows:
            yield row[0], row[1]

    async def insert_callback_value(self, value: dict | None) -> str:
        row = await self.database.query_row_must('''
            INSERT INTO callback_data(value)
            VALUES($1)
            ON CONFLICT (value) DO UPDATE set value=callback_data.value
            RETURNING uuid
        ''', (value,))
        return str(row[0])
