from datetime import datetime

import pytest
import telegram

from toxicbot.config import ConfigFactory
from toxicbot.db import DatabaseFactory, Database
from toxicbot.handlers.database import DatabaseUpdateSaver
from toxicbot.metrics import Metrics


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


@pytest.fixture
def dus(database: Database):
    metrics = Metrics()
    return DatabaseUpdateSaver(database, metrics)


def test_message_handle(database: Database, dus: DatabaseUpdateSaver):
    chat = telegram.Chat(id=11, type='bla', title='chat title')
    from_user = telegram.User(id=14, first_name='Elisey', is_bot=False)
    message = telegram.Message(message_id=22, date=datetime.now(), chat=chat, from_user=from_user)
    update = telegram.Update(update_id=1337, message=message)

    dus.handle(update)

    rows = database.query_row('''SELECT chat_id FROM updates WHERE tg_id=%s''', (1337,))
    assert rows is not None
    assert len(rows) == 1
    assert rows[0] == 11
