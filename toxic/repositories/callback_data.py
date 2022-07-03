import json

from toxic.db import Database


class CallbackDataRepository:
    def __init__(self, database: Database):
        self.database = database

    async def insert_value(self, value: dict | None) -> str:
        row = await self.database.query_row('''
            INSERT INTO callback_data(value)
            VALUES($1)
            ON CONFLICT (value) DO UPDATE set value=callback_data.value
            RETURNING uuid
        ''', (json.dumps(value),))
        return str(row[0])

    async def get_value(self, uuid: str) -> dict | None:
        row = await self.database.query_row('SELECT value FROM callback_data WHERE uuid=$1', (uuid,))
        if row is None:
            return None

        return row[0]
