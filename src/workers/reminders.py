import time
from datetime import datetime

from src import db
from src.helpers import general
from src.helpers.log import print_sleep
from src.workers.worker import Worker


def until(dt: datetime) -> float:
    return time.mktime(dt.timetuple()) - datetime.utcnow().timestamp()


class ReminderWorker(Worker):
    def work(self):
        while True:
            with db.conn, db.conn.cursor() as cur:
                cur.execute('SELECT id, chat_id, datetime, text FROM reminders WHERE isactive ORDER BY datetime LIMIT 1;')

                record = cur.fetchone()
                if record is None:
                    break

                id, chat_id, dt, text = record

            seconds = until(dt)
            if seconds > 0:
                print_sleep(seconds, f'reminder #{id}')
                time.sleep(seconds)

            general.send(chat_id, text)

            with db.conn, db.conn.cursor() as cur:
                cur.execute('UPDATE reminders SET isactive=FALSE WHERE id = %s', (id,))
