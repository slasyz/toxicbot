from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import AsyncIterator

from loguru import logger

from toxic.db import Database


CACHE_DURATION = timedelta(seconds=5)


class ChatsRepository:
    def __init__(self, database: Database):
        self.database = database

    async def get_latest_chat_id(self, chat_id: int) -> int:
        row = await self.database.query_row('''
            WITH RECURSIVE r AS (
                SELECT tg_id, next_tg_id
                FROM chats
                WHERE tg_id=$1
                UNION
                SELECT chats.tg_id, chats.next_tg_id
                FROM chats
                    JOIN r ON r.next_tg_id=chats.tg_id
            )
            SELECT tg_id, next_tg_id
            FROM r
            WHERE next_tg_id IS NULL;
        ''', (chat_id,))
        return row[0]

    async def get_period(self, chat_id: int) -> int:
        row = await self.database.query_row('''SELECT chain_period FROM chats WHERE tg_id = $1''', (chat_id,))
        return row[0]

    async def count_messages(self, chat_id: int) -> int:
        row = await self.database.query_row('''SELECT count(tg_id) FROM messages WHERE chat_id = $1''', (chat_id,))
        return row[0]

    async def get_stat(self, chat_id: int) -> AsyncIterator[tuple[str, int]]:
        rows = await self.database.query('''
                WITH RECURSIVE ch(id) AS (
                    SELECT $1::bigint
                    UNION
                    SELECT c.tg_id
                    FROM chats c
                        JOIN ch ON c.next_tg_id=ch.id OR
                                   (c.tg_id=ch.id AND c.next_tg_id IS NOT NULL)
                )
                SELECT btrim(concat(u.first_name, ' ', u.last_name)), count(m.*) as c
                FROM messages m
                    JOIN users u ON m.user_id = u.tg_id
                    JOIN ch ON chat_id=ch.id
                GROUP BY user_id, u.first_name, u.last_name
                ORDER BY c DESC
                LIMIT 10;
            ''', (chat_id,))
        for row in rows:
            yield row[0], row[1]

    async def list(self) -> AsyncIterator[tuple[int, str]]:
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

    async def is_existing(self, chat_id: int) -> bool:
        row = await self.database.query_row('SELECT tg_id FROM chats WHERE tg_id=$1', (chat_id,))
        return row is not None

    async def update_next_id(self, chat_id: int, new_chat_id: int):
        await self.database.exec('UPDATE chats SET next_tg_id = $1 WHERE tg_id=$2', (new_chat_id, chat_id))

    async def disable_joke(self, chat_id):
        await self.database.exec('UPDATE chats SET joke_period=0 WHERE tg_id=$1', (chat_id,))

    async def get_joker_chats(self) -> AsyncIterator[tuple[int, int]]:
        rows = await self.database.query('SELECT tg_id, joke_period FROM chats WHERE tg_id < 0 AND joke_period > 0;')
        for row in rows:
            yield row[0], row[1]


@dataclass
class CachedEntry:
    latest_chat_id: int
    valid_until: datetime


class CachedChatsRepository(ChatsRepository):
    def __init__(self, database: Database):
        super().__init__(database)
        self.latest_id_cache: dict[int, CachedEntry] = {}

    async def get_latest_chat_id(self, chat_id: int) -> int:
        entry = self.latest_id_cache.get(chat_id)
        if entry is not None and entry.valid_until > datetime.now():
            return entry.latest_chat_id

        logger.debug('Cache miss for chat_id=%s.', chat_id)
        latest_chat_id = await super().get_latest_chat_id(chat_id)
        self.latest_id_cache[chat_id] = CachedEntry(latest_chat_id, datetime.now() + CACHE_DURATION)
        return latest_chat_id
