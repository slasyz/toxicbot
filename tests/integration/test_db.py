import pytest
import telegram

from toxicbot.config import ConfigFactory
from toxicbot.db import DatabaseFactory


@pytest.fixture
def database():
    config = ConfigFactory().load(['/app/config.tests.json'])

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
def test_database_query(query, vars, expected, database):
    rows = list(database.query(query, vars))
    assert rows == expected
