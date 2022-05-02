import json

from toxic.db import Database


class CallbackDataRepository:
    def __init__(self, database: Database):
        self.database = database

    def insert_value(self, value: dict | None) -> str:
        return self.database.query_row('''
            INSERT INTO callback_data(value)
            VALUES(%s)
            ON CONFLICT (value) DO UPDATE set value=callback_data.value
            RETURNING uuid
        ''', (json.dumps(value),))[0]

    def get_value(self, uuid: str) -> dict | None:
        row = self.database.query_row('SELECT value FROM callback_data WHERE uuid=%s', (uuid,))
        if row is None:
            return None

        return row[0]
