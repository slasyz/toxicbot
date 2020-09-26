#!/usr/bin/env python3

import os
import time
import logging as pylogging

import telegram
from telegram.error import NetworkError, Unauthorized, Conflict

from src import config, db, handling
from src.helpers import logging, general
from src.server import server
from src.tasks import anecdotes, reminders


def __main__():
    logging.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()

    config.load('./config.json')
    db.connect()
    server.listen()
    anecdotes.start_worker()
    reminders.start_worker()
    handling.init()

    general.bot = telegram.Bot(config.c['telegram']['token'])

    # TODO: распутать это всё
    update_id = None
    while True:
        try:
            for update in general.bot.get_updates(offset=update_id, timeout=10):
                update_id = update.update_id
                handling.handle_update(update)
                update_id = update.update_id + 1
        except NetworkError as e:
            pylogging.error(f'network error: {e}')
            if isinstance(e, telegram.error.BadRequest):
                update_id += 1
            time.sleep(1)
        except Unauthorized:  # The user has removed or blocked the bot.
            pylogging.info("user removed or blocked the bot")
            update_id += 1
        except Conflict:
            pylogging.error("bot is already running somewhere, stopping it")
            exit(1)
        except KeyboardInterrupt:
            exit(0)


if __name__ == '__main__':
    __main__()
