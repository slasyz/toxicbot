import gzip
from typing import List

import yaml

from src import db


def get_total() -> int:
    with db.conn, db.conn.cursor() as cur:
        cur.execute('SELECT count(tg_id) FROM updates WHERE json IS NULL')
        return cur.fetchone()[0]


def load(limit: int) -> List:
    res = []

    with db.conn, db.conn.cursor() as cur:
        cur.execute('SELECT tg_id, dump FROM updates WHERE json IS NULL ORDER BY tg_id LIMIT %s', (limit,))
        for update_id, dump in cur:
            dump = gzip.decompress(dump.tobytes())
            dump = yaml.load(dump.decode('utf-8'), yaml.UnsafeLoader)

            res.append((update_id, dump.to_json()))

    return res


def save(src: List):
    for update_id, dump in src:
        with db.conn, db.conn.cursor() as cur:
            cur.execute('UPDATE updates SET json = %s WHERE tg_id = %s', (dump, update_id))


def __main__():
    import main  # pylint: disable=import-outside-toplevel
    main.init()

    total = get_total()

    cnt = 0
    while True:
        updates = load(100)
        if len(updates) == 0:
            return

        save(updates)
        cnt += len(updates)

        print(cnt, '/', total)


if __name__ == '__main__':
    __main__()
