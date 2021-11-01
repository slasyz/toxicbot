import json
from typing import Optional

from toxic.db import Database


class CallbackDataRepository:
    def __init__(self, database: Database):
        self.database = database

    def insert_value(self, value: Optional[dict]) -> int:
        return self.database.query_row('''
            INSERT INTO callback_data(value)
            VALUES(%s)
            ON CONFLICT (value) DO UPDATE set value=callback_data.value
            RETURNING id
        ''', (json.dumps(value),))[0]

    def get_value(self, id: int) -> Optional[dict]:
        row = self.database.query_row('SELECT value FROM callback_data WHERE id=%s', (id,))
        if row is None:
            return None

        return row[0]
