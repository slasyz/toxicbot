import threading
import time
from datetime import datetime

from src import db, helpers
from src.logging import print_sleep


def until(dt: datetime) -> float:
    return time.mktime(dt.timetuple()) - datetime.utcnow().timestamp()


def worker():
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

        helpers.send_message(chat_id, text)

        with db.conn, db.conn.cursor() as cur:
            cur.execute('UPDATE reminders SET isactive=FALSE WHERE id = %s', (id,))


def start_worker():
    threading.Thread(target=worker).start()
