import re
from typing import Optional

import telegram

from toxicbot import db

LINK_REGEXP = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')

bot: Optional[telegram.Bot] = None


def is_admin(user_id: int) -> bool:
    with db.conn, db.conn.cursor() as cur:
        cur.execute('SELECT true FROM users WHERE tg_id=%s AND admin', (user_id,))
        return cur.fetchone() is not None
