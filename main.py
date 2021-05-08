#!/usr/bin/env python3

import os
import sys
import time
import logging

import telegram
from telegram.error import NetworkError, Unauthorized, Conflict

from toxicbot import config, db, handling
from toxicbot.helpers import log, general, messages
from toxicbot.workers import worker
from toxicbot.workers.jokes import JokesWorker
from toxicbot.workers.reminders import ReminderWorker
from toxicbot.workers.server.server import ServerWorker


def init(config_file):
    log.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()  # pylint: disable=no-member

    config.load(config_file)
    db_config = config.get_database_creds()
    db.connect(db_config.host, db_config.port, db_config.database, db_config.user, db_config.password)


def __main__():
    init('./config.json')

    general.bot = telegram.Bot(config.get_telegram_token())

    worker.start_workers([ServerWorker(), JokesWorker(), ReminderWorker()])
    handling.init()

    messages.send_to_admins('Я запустился.')

    # TODO: распутать это всё
    update_id = None
    while True:
        try:
            for update in general.bot.get_updates(offset=update_id, timeout=10):
                update_id = update.update_id
                handling.handle_update(update)
                update_id = update.update_id + 1
        except NetworkError as ex:
            logging.error('network error: %s', ex)
            if isinstance(ex, telegram.error.BadRequest):
                update_id += 1
            time.sleep(1)
        except Unauthorized:  # The user has removed or blocked the bot.
            logging.info('user removed or blocked the bot')
            update_id += 1
        except Conflict:
            logging.error('bot is already running somewhere, stopping it')
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    __main__()
