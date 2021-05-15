#!/usr/bin/env python3

import os
import sys
import time
import logging
from typing import Tuple

import sentry_sdk
import telegram
from prometheus_client import start_http_server
from telegram.error import NetworkError, Unauthorized, Conflict

from toxicbot.config import ConfigFactory, Config
from toxicbot.db import Database, DatabaseFactory
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
from toxicbot.handlers.database import DatabaseUpdateManager
from toxicbot.handling import CommandDefinition, HandlersManager
from toxicbot.helpers import log
from toxicbot.helpers.messages import Bot
from toxicbot.metrics import Metrics
from toxicbot.workers import worker
from toxicbot.workers.jokes import JokesWorker
from toxicbot.workers.reminders import ReminderWorker
from toxicbot.workers.server.server import ServerWorker, Server


def init(config_files: list) -> Tuple[Config, Database, Bot, Metrics, DatabaseUpdateManager]:
    log.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()  # pylint: disable=no-member

    config = ConfigFactory().load(config_files)

    database = DatabaseFactory().connect(
        config['database']['host'],
        config['database']['port'],
        config['database']['name'],
        config['database']['user'],
        config['database']['pass'],
    )

    metrics = Metrics()

    dum = DatabaseUpdateManager(database, metrics)

    telegram_bot = telegram.Bot(config['telegram']['token'])
    bot = Bot(telegram_bot, database, dum)

    return config, database, bot, metrics, dum


def __main__():
    # TODO: use dependency injection tool
    # TODO: inconsistency between factory constructor args and method args: Factory(X).create() vs Factory().create(X)
    config, database, bot, metrics, dum = init(['./config.json', '/etc/toxic/config.json'])

    sentry_sdk.init(config['sentry']['dsn'])  # pylint: disable=abstract-class-instantiated
    start_http_server(config['prometheus']['port'])

    joker = JokerFactory().create(config['replies']['joker'])

    server = Server(config['server']['host'], config['server']['port'], database)

    worker.start_workers([
        ServerWorker(server),
        JokesWorker(joker, database, bot),
        ReminderWorker(database, bot),
    ], bot)

    handlers_private = (
        PrivateHandler(config['replies']['private'], database, bot),
    )

    splitter = PunctuationSplitter()
    textizer = Textizer(Featurizer(), splitter, metrics)
    chain_factory = ChainFactory(window=3)

    handlers_chats = (
        VoiceHandlerFactory().create(config['replies']['voice'], bot),
        KeywordsHandlerFactory().create(config['replies']['keywords'], bot),
        SorryHandlerFactory().create(config['replies']['sorry'], bot),
        StatsHandlerFactory().create(config['replies']['stats'], database, bot),
        ChainHandlerFactory(chain_factory, textizer, database, bot).create(),
    )

    commands = (
        CommandDefinition('dump', DumpCommand(database, bot), True),
        CommandDefinition('stat', StatCommand(database, bot), False),
        CommandDefinition('joke', JokeCommand(joker, bot), False),
        CommandDefinition('send', SendCommand(database, bot), True),
        CommandDefinition('chats', ChatsCommand(database, bot), True),
    )
    handle_manager = HandlersManager(
        handlers_private,
        handlers_chats,
        commands,
        database,
        bot,
        dum,
        metrics,
    )

    bot.send_to_admins('Я запустился.')

    messages_total_row = database.query_row('''SELECT count(*) FROM messages''')
    metrics.messages.set(messages_total_row[0])

    # TODO: распутать это всё
    update_id = None
    while True:
        try:
            # TODO: bot.bot bad
            for update in bot.bot.get_updates(offset=update_id, timeout=10):
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
