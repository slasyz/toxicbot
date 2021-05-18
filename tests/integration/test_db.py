from toxicbot.config import ConfigFactory
from toxicbot.db import DatabaseFactory


def test_database_query():
    config = ConfigFactory().load(['/app/config.tests.json'])

    db = DatabaseFactory().connect(
        config['database']['host'],
        config['database']['port'],
        config['database']['name'],
        config['database']['user'],
        config['database']['pass'],
    )

    rows = list(db.query('SELECT %s;', (1337,)))

    assert len(rows) == 1
    assert rows[0][0] == 1337
