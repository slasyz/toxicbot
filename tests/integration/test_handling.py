import asyncio
from datetime import datetime

import pytest
import aiogram

from toxic.config import Config
from toxic.db import Database
from toxic.handlers.database import DatabaseUpdateSaver
from toxic.metrics import Metrics


@pytest.fixture
async def database():
    config = Config.load(['config.tests.json'])

    return await Database.connect(
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


async def test_message_handle(database: Database, dus: DatabaseUpdateSaver):
    chat = aiogram.types.Chat(id=11, type='bla', title='chat title')
    from_user = aiogram.types.User(id=14, first_name='Elisey', is_bot=False)
    message = aiogram.types.Message(message_id=22, date=datetime.now().timestamp(), chat=chat, from_user=from_user)
    update = aiogram.types.Update(update_id=1337, message=message)

    asyncio.run(dus.handle(update))

    rows = await database.query_row('''SELECT chat_id FROM updates WHERE tg_id=%s''', (1337,))
    assert rows is not None
    assert len(rows) == 1
    assert rows[0] == 11
