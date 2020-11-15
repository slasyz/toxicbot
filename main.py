#!/usr/bin/env python3

import os
import sys
import time
import logging

import telegram
from telegram.error import NetworkError, Unauthorized, Conflict

from src import config, db, handling
from src.helpers import log, general
from src.workers import worker
from src.workers.jokes import JokesWorker
from src.workers.reminders import ReminderWorker
from src.workers.server.server import ServerWorker


def init():
    log.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()  # pylint: disable=no-member

    config.load('./config.json')
    db.connect()
    worker.start_workers([ServerWorker(), JokesWorker(), ReminderWorker()])
    handling.init()


def __main__():
    init()

    general.bot = telegram.Bot(config.c['telegram']['token'])

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
            logging.info("user removed or blocked the bot")
            update_id += 1
        except Conflict:
            logging.error("bot is already running somewhere, stopping it")
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    __main__()
