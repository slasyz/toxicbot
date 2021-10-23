from __future__ import annotations

import logging
from datetime import datetime, timedelta
from collections.abc import Iterator

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

    def get_period(self, chat_id: int) -> int:
        return self.database.query_row('''SELECT chain_period FROM chats WHERE tg_id = %s''', (chat_id,))[0]

    def count_messages(self, chat_id: int) -> int:
        row = self.database.query_row('''SELECT count(tg_id) FROM messages WHERE chat_id = %s''', (chat_id,))
        return row[0]

    def get_stat(self, chat_id: int) -> Iterator[tuple[str, int]]:
        rows = self.database.query('''
                SELECT btrim(concat(u.first_name, ' ', u.last_name)), count(m.*) as c
                FROM messages m
                    JOIN users u on m.user_id = u.tg_id
                WHERE chat_id=%s
                GROUP BY user_id, u.first_name, u.last_name
                ORDER BY c DESC
                LIMIT 10;
            ''', (chat_id,))
        for row in rows:
            yield row[0], row[1]

    def list(self) -> Iterator[tuple[int, str]]:
        rows = self.database.query('''
                    SELECT c.tg_id, c.title
                    FROM chats c
                    WHERE c.tg_id < 0
                    UNION
                    SELECT u.tg_id, btrim(concat(u.first_name, ' ', u.last_name))
                    FROM users u
                ''')
        for row in rows:
            yield row[0], row[1]

    def is_existing(self, chat_id: int) -> bool:
        row = self.database.query('SELECT tg_id FROM chats WHERE tg_id=%s', (chat_id,))
        return row is not None

    def update_next_id(self, chat_id: int, new_chat_id: int):
        self.database.exec('UPDATE chats SET next_tg_id = %s WHERE tg_id=%s', (new_chat_id, chat_id))

    def get_joker_chats(self) -> Iterator[int]:
        rows = self.database.query('SELECT tg_id FROM chats WHERE tg_id < 0 AND joke;')
        for row in rows:
            yield row[0]


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
