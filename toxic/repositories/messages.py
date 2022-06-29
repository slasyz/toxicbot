from typing import AsyncIterator

from toxic.db import Database


class MessagesRepository:
    def __init__(self, database: Database):
        self.database = database

    async def get_all_groups_messages(self) -> AsyncIterator[tuple[int, str | None]]:
        for row in await self.database.query_async('''
                SELECT chat_id, text 
                FROM messages 
                WHERE chat_id < 0 AND update_id IS NOT NULL 
                ORDER BY tg_id'''):
            yield row[0], row[1]

    async def get_update_dump(self, update_id: int) -> str | None:
        row = await self.database.query_row_async('SELECT json FROM updates WHERE tg_id=$1', (update_id,))
        if row is None:
            return None

        return row[0]

    async def get_text(self, chat_id: int, message_id: int) -> str | None:
        row = await self.database.query_row_async('SELECT text FROM messages WHERE chat_id=$1 AND tg_id=$2', (chat_id, message_id))
        if row is None:
            return None

        return row[0]
