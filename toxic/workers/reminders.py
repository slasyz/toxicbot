import time
from datetime import datetime

from toxic.db import Database
from toxic.helpers.log import print_sleep
from toxic.messenger import Messenger
from toxic.workers.worker import Worker


def until(dt: datetime) -> float:
    return time.mktime(dt.timetuple()) - datetime.utcnow().timestamp()


class ReminderWorker(Worker):
    def __init__(self, database: Database, messenger: Messenger):
        self.database = database
        self.messenger = messenger

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

            self.messenger.send(chat_id, text)

            self.database.exec('UPDATE reminders SET isactive=FALSE WHERE id = %s', (id,))
