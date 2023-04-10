from typing import AsyncIterator

from toxic.db import Database


class MessagesRepository:
    def __init__(self, database: Database):
        self.database = database

    async def get_all_groups_messages(self) -> AsyncIterator[tuple[int, str | None]]:
        for row in await self.database.query('''
                SELECT chat_id, text 
                FROM messages 
                WHERE chat_id < 0 AND update_id IS NOT NULL 
                ORDER BY tg_id'''):
            yield row[0], row[1]

    async def get_all_user_replies(self, user_id_from: int, user_id_to: int) -> AsyncIterator[tuple[int, str]]:
        for row in await self.database.query('''
                SELECT m.chat_id, m.text
                FROM messages m
                    JOIN updates u on m.update_id = u.tg_id
                WHERE
                    m.chat_id < 0 AND
                    user_id = $1 AND
                    text IS NOT NULL AND text != '' AND
                    (u.json->'message'->'reply_to_message'->'from'->'id')::bigint = $2
                ORDER BY m.tg_id''', (user_id_from, user_id_to)):
            yield row[0], row[1]

    async def get_update_dump(self, update_id: int) -> str | None:
        row = await self.database.query_row('SELECT json FROM updates WHERE tg_id=$1', (update_id,))
        if row is None:
            return None

        return row[0]

    async def get_text(self, chat_id: int, message_id: int) -> str | None:
        row = await self.database.query_row('SELECT text FROM messages WHERE chat_id=$1 AND tg_id=$2', (chat_id, message_id))
        if row is None:
            return None

        return row[0]
