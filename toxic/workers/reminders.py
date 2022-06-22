import asyncio
import time
from datetime import datetime

from toxic.helpers.log import print_sleep
from toxic.messenger.messenger import Messenger
from toxic.repositories.reminders import RemindersRepository
from toxic.workers.worker import Worker


def until(when: datetime) -> float:
    return time.mktime(when.timetuple()) - datetime.utcnow().timestamp()


class ReminderWorker(Worker):
    def __init__(self, reminders_repo: RemindersRepository, messenger: Messenger):
        self.reminders_repo = reminders_repo
        self.messenger = messenger

    async def work(self):
        while True:
            reminder = await self.reminders_repo.get_latest_reminder()
            if reminder is None:
                return

            seconds = until(reminder.when)
            if seconds > 0:
                print_sleep(seconds, f'reminder #{id}')
                await asyncio.sleep(seconds)

            await self.messenger.send(reminder.chat_id, reminder.text)
            await self.reminders_repo.deactivate_reminder(reminder.id)
