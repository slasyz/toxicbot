#!/usr/bin/env python3

import os
import time
import logging as pylogging

import telegram
from telegram.error import NetworkError, Unauthorized, Conflict

from src import config, db, helpers, logging, handling
from src.server import server
from src.tasks import anecdotes


def __main__():
    logging.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()

    config.load('./config.json')
    db.connect()
    server.listen()
    anecdotes.start_worker()
    handling.init()

    helpers.bot = telegram.Bot(config.c['telegram']['token'])

    update_id = None
    while True:
        try:
            for update in helpers.bot.get_updates(offset=update_id, timeout=10):
                handling.handle_update(update)
                update_id = update.update_id + 1
        except NetworkError:
            time.sleep(1)
        except Unauthorized:  # The user has removed or blocked the bot.
            update_id += 1
        except Conflict:
            pylogging.error("bot is already running somewhere, stopping it")
            exit(1)
        except KeyboardInterrupt:
            exit(0)


if __name__ == '__main__':
    __main__()
