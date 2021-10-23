from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from toxic.db import Database


@dataclass
class Reminder:
    id: int
    chat_id: int
    when: datetime
    text: str


class RemindersRepository:
    def __init__(self, database: Database):
        self.database = database

    def get_latest_reminder(self) -> Optional[Reminder]:
        row = self.database.query_row('SELECT id, chat_id, datetime, text FROM reminders WHERE isactive ORDER BY datetime LIMIT 1;')
        if row is None:
            return None
        return Reminder(
            row[0],
            row[1],
            row[2],
            row[3]
        )

    def deactivate_reminder(self, id: int):
        self.database.exec('UPDATE reminders SET isactive=FALSE WHERE id = %s', (id,))
