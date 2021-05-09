#!/usr/bin/env python3

import os
import sys
import time
import logging

import sentry_sdk
import telegram
from telegram.error import NetworkError, Unauthorized, Conflict

from toxicbot import config, db
from toxicbot.features.chain.chain import ChainFactory
from toxicbot.features.chain.featurizer import Featurizer
from toxicbot.features.chain.textizer import Textizer
from toxicbot.features.joke import JokerFactory
from toxicbot.handlers.chain import ChainHandlerFactory
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


def init(config_files: list):
    log.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()  # pylint: disable=no-member

    c = config.load(config_files)

    sentry_sdk.init(c['sentry']['dsn'])  # pylint: disable=abstract-class-instantiated

    db.connect(
        c['database']['host'],
        c['database']['port'],
        c['database']['name'],
        c['database']['user'],
        c['database']['pass'],
    )

    general.bot = telegram.Bot(c['telegram']['token'])

    return c


def __main__():
    c = init(['./config.json', '/etc/toxic/config.json'])

    joker = JokerFactory().create(c['replies']['joker'])

    worker.start_workers([
        ServerWorker(c['server']['host'], c['server']['port']),
        JokesWorker(joker),
        ReminderWorker(),
    ])

    handlers_private = (
        PrivateHandler(c['replies']['private']),
    )

    splitter = PunctuationSplitter()
    textizer = Textizer(Featurizer(), splitter)
    chain_factory = ChainFactory(window=3)

    handlers_chats = (
        VoiceHandlerFactory().create(c['replies']['voice']),
        KeywordsHandlerFactory().create(c['replies']['keywords']),
        SorryHandlerFactory().create(c['replies']['sorry']),
        StatsHandlerFactory().create(c['replies']['stats']),
        ChainHandlerFactory(chain_factory, textizer).create(),
    )

    commands = (
        CommandDefinition('dump', DumpCommand(), True),
        CommandDefinition('stat', StatCommand(), False),
        CommandDefinition('joke', JokeCommand(joker), False),
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
