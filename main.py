#!/usr/bin/env python3

import os
import sys
import time
import logging

import telegram
from telegram.error import NetworkError, Unauthorized, Conflict

from toxicbot import config, db
from toxicbot.handlers.chain import ChainHandler
from toxicbot.features.chain.splitters import PunctuationSplitter
from toxicbot.handlers.commands.joke import JokeCommand
from toxicbot.handlers.commands.chats import ChatsCommand
from toxicbot.handlers.commands.dump import DumpCommand
from toxicbot.handlers.commands.send import SendCommand
from toxicbot.handlers.commands.stat import StatCommand, StatsHandlerFactory
from toxicbot.handlers.chat_replies import PrivateHandler, VoiceHandlerFactory, KeywordsHandlerFactory, SorryHandlerFactory
from toxicbot.handling import CommandDefinition, HandlersManager
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
    db.connect(
        config.c['database']['host'],
        config.c['database']['port'],
        config.c['database']['name'],
        config.c['database']['user'],
        config.c['database']['pass'],
    )

    general.bot = telegram.Bot(config.c['telegram']['token'])


def __main__():
    init('./config.json')

    worker.start_workers([ServerWorker(), JokesWorker(), ReminderWorker()])

    handlers_private = (
        PrivateHandler(config.c['replies']['private']),
    )

    handlers_chats = (
        VoiceHandlerFactory().create(config.c['replies']['voice']),
        KeywordsHandlerFactory().create(config.c['replies']['keywords']),
        SorryHandlerFactory().create(config.c['replies']['sorry']),
        StatsHandlerFactory().create(config.c['replies']['stats']),
        ChainHandler(window=3, splitter=PunctuationSplitter()),
    )

    commands = (
        CommandDefinition('dump', DumpCommand(), True),
        CommandDefinition('stat', StatCommand(), False),
        CommandDefinition('joke', JokeCommand(), False),
        CommandDefinition('send', SendCommand(), True),
        CommandDefinition('chats', ChatsCommand(), True),
    )
    handle_manager = HandlersManager(handlers_private, handlers_chats, commands)

    messages.send_to_admins('Я запустился.')

    # TODO: распутать это всё
    update_id = None
    while True:
        try:
            for update in general.bot.get_updates(offset=update_id, timeout=10):
                update_id = update.update_id
                handle_manager.handle_update(update)
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
