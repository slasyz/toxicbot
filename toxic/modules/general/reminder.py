import asyncio
import time
from dataclasses import dataclass
from datetime import datetime

from toxic.db import Database
from toxic.helpers.log import print_sleep
from toxic.interfaces import Worker
from toxic.messenger.messenger import Messenger


@dataclass
class Reminder:
    id: int
    chat_id: int
    when: datetime
    text: str


def until(when: datetime) -> float:
    return time.mktime(when.timetuple()) - datetime.utcnow().timestamp()


class ReminderWorker(Worker):
    def __init__(self, database: Database, messenger: Messenger):
        self.database = database
        self.messenger = messenger

    async def get_latest_reminder(self) -> Reminder | None:
        row = await self.database.query_row('SELECT id, chat_id, datetime, text FROM reminders WHERE isactive ORDER BY datetime LIMIT 1;')
        if row is None:
            return None
        return Reminder(
            row[0],
            row[1],
            row[2],
            row[3]
        )

    async def deactivate_reminder(self, id: int):
        await self.database.exec('UPDATE reminders SET isactive=FALSE WHERE id = $1', (id,))

    async def work(self):
        while True:
            reminder = await self.get_latest_reminder()
            if reminder is None:
                return

            seconds = until(reminder.when)
            if seconds > 0:
                print_sleep(seconds, f'reminder #{id}')
                await asyncio.sleep(seconds)

            await self.messenger.send(reminder.chat_id, reminder.text)
            await self.deactivate_reminder(reminder.id)
