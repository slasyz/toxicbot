import pytest
import pytest_asyncio

from toxic.config import Config
from toxic.db import Database


@pytest_asyncio.fixture
async def database():
    config = Config.load(['config.tests.json'])

    return await Database.connect(
        config['database']['host'],
        config['database']['port'],
        config['database']['name'],
        config['database']['user'],
        config['database']['pass'],
    )


@pytest.mark.parametrize(
    ['query', 'vars', 'expected'],
    [
        ('SELECT $1::int;', (1337,), [(1337,)]),
        ('SELECT $1::jsonb;', ({"a": "b", "c": "d"},), [({'a': 'b', 'c': 'd'},)])
    ]
)
async def test_database_query(query: str, vars: tuple, expected: list[tuple], database: Database):
    rows = [x for x in await database.query(query, vars)]
    assert rows == expected


async def test_database_insert(database: Database):
    await database.exec('DELETE FROM reminders WHERE chat_id=1235')
    await database.exec('DELETE FROM chats WHERE tg_id=1235')

    await database.exec("INSERT INTO chats(tg_id, title) VALUES(1235, 'chat title')")

    row_insert = await database.query_row("INSERT INTO reminders(chat_id, datetime, text, isactive) VALUES(1235, now(), 'asdf', TRUE) RETURNING id")
    assert row_insert is not None

    row_select = await database.query_row("SELECT text FROM reminders WHERE id=$1", (row_insert[0],))
    assert row_select is not None
    assert row_select[0] == 'asdf'
