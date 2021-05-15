import time
from datetime import datetime

from toxicbot.db import Database
from toxicbot.helpers.log import print_sleep
from toxicbot.helpers.messages import Bot
from toxicbot.workers.worker import Worker


def until(dt: datetime) -> float:
    return time.mktime(dt.timetuple()) - datetime.utcnow().timestamp()


class ReminderWorker(Worker):
    def __init__(self, database: Database, bot: Bot):
        self.database = database
        self.bot = bot

    def work(self):
        while True:
            row = self.database.query_row('SELECT id, chat_id, datetime, text FROM reminders WHERE isactive ORDER BY datetime LIMIT 1;')
            if row is None:
                break
            id, chat_id, dt, text = row

            seconds = until(dt)
            if seconds > 0:
                print_sleep(seconds, f'reminder #{id}')
                time.sleep(seconds)

            self.bot.send(chat_id, text)

            self.database.query('UPDATE reminders SET isactive=FALSE WHERE id = %s', (id,))
