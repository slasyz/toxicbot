import logging
from datetime import datetime, timedelta

from dataclasses import dataclass

from toxic.db import Database


CACHE_DURATION = timedelta(seconds=5)


class ChatsRepository:
    def __init__(self, database: Database):
        self.database = database

    def get_latest_chat_id(self, chat_id: int) -> int:
        row = self.database.query_row('''
            WITH RECURSIVE r AS (
                SELECT tg_id, next_tg_id
                FROM chats
                WHERE tg_id=%s
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


@dataclass
class CachedEntry:
    latest_chat_id: int
    valid_until: datetime


class CachedChatsRepository(ChatsRepository):
    def __init__(self, database: Database):
        super().__init__(database)
        self.latest_id_cache: dict[int, CachedEntry] = {}

    def get_latest_chat_id(self, chat_id: int) -> int:
        entry = self.latest_id_cache.get(chat_id)
        if entry is not None and entry.valid_until > datetime.now():
            return entry.latest_chat_id

        logging.debug('Cache miss for chat_id=%s', chat_id)
        latest_chat_id = super().get_latest_chat_id(chat_id)
        self.latest_id_cache[chat_id] = CachedEntry(latest_chat_id, datetime.now() + CACHE_DURATION)
        return latest_chat_id
