import pytest
import telegram

from toxic.config import ConfigFactory
from toxic.db import DatabaseFactory, Database


@pytest.fixture
def database():
    config = ConfigFactory().load(['config.tests.json'])

    return DatabaseFactory().connect(
        config['database']['host'],
        config['database']['port'],
        config['database']['name'],
        config['database']['user'],
        config['database']['pass'],
    )


@pytest.mark.parametrize(
    ['query', 'vars', 'expected'],
    [
        ('SELECT %s;', (1337,), [(1337,)]),
        ('SELECT %(name)s;', {'name': 'Vyacheslav'}, [('Vyacheslav',)]),
        ('SELECT %(id)s, %(first_name)s, %(is_bot)s;', telegram.User(id=1234, first_name='Vyacheslav', is_bot=False), [(1234, 'Vyacheslav', False)]),
    ]
)
def test_database_query(query, vars, expected, database: Database):
    rows = list(database.query(query, vars))
    assert rows == expected


def test_database_insert(database: Database):
    row_insert = database.exec("INSERT INTO chats(tg_id, title) VALUES(1235, 'chat title')")
    assert row_insert is None

    row_insert = database.query_row("INSERT INTO reminders(chat_id, datetime, text, isactive) VALUES(1235, now(), 'asdf', TRUE) RETURNING id")
    assert row_insert is not None

    row_select = database.query_row("SELECT text FROM reminders WHERE id=%s", (row_insert[0],))
    assert row_select is not None
    assert row_select[0] == 'asdf'
