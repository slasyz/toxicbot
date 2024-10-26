from toxic.db import Database


class CallbackDataRepository:
    def __init__(self, database: Database):
        self.database = database

    async def insert_value(self, value: dict | None) -> str:
        row = await self.database.query_row_must('''
            INSERT INTO callback_data(value)
            VALUES($1)
            ON CONFLICT (value) DO UPDATE set value=callback_data.value
            RETURNING uuid
        ''', (value,))
        return str(row[0])
