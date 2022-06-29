import json

from toxic.db import Database


class SettingsRepository:
    def __init__(self, database: Database):
        self.database = database

    async def _set_value(self, key: str, value: str | None):
        if value is None:
            await self.database.exec('DELETE FROM settings WHERE key=$1', (key,))
            return

        await self.database.exec('''
            INSERT INTO settings(key, value) 
            VALUES($1, $2)
            ON CONFLICT(key) DO UPDATE
                SET value = $3
        ''', (key, value, value))

    async def _get_value(self, key: str) -> str | None:
        row = await self.database.query_row('SELECT value FROM settings WHERE key=$1', (key,))
        if row is None:
            return None

        return row[0]

    async def spotify_get_token(self) -> dict | None:
        value_str = await self._get_value('spotify_token')
        if value_str is None:
            return None

        return json.loads(value_str)

    async def spotify_set_token(self, token_info: dict):
        value_str = json.dumps(token_info)
        return await self._set_value('spotify_token', value_str)
