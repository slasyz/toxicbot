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

from toxic.config import ConfigFactory, Config
from toxic.db import Database, DatabaseFactory
from toxic.features.chain.chain import ChainFactory
from toxic.features.chain.featurizer import Featurizer
from toxic.features.chain.textizer import Textizer
from toxic.features.joke import JokerFactory
from toxic.features.odesli import Odesli
from toxic.handlers.chain import ChainHandlerFactory
from toxic.features.chain.splitters import SpaceAdjoinSplitter
from toxic.handlers.commands.joke import JokeCommand
from toxic.handlers.commands.chats import ChatsCommand
from toxic.handlers.commands.dump import DumpCommand
from toxic.handlers.commands.send import SendCommand
from toxic.handlers.commands.stat import StatCommand, StatsHandlerFactory
from toxic.handlers.chat_replies import PrivateHandler, VoiceHandlerFactory, KeywordsHandlerFactory, SorryHandlerFactory
from toxic.handlers.commands.voice import VoiceCommand
from toxic.handlers.database import DatabaseUpdateSaver
from toxic.handlers.music import MusicHandler
from toxic.handling import CommandDefinition, HandlersManager
from toxic.helpers import log
from toxic.helpers.delayer import DelayerFactory
from toxic.helpers.rate_limiter import RateLimiter
from toxic.messenger import Messenger
from toxic.metrics import Metrics
from toxic.workers.jokes import JokesWorker
from toxic.workers.reminders import ReminderWorker
from toxic.workers.server.server import ServerWorker, Server
from toxic.workers.worker import WorkersManager


def init(config_files: list) -> Tuple[Config, Database, Messenger, Metrics, DatabaseUpdateSaver]:
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

    dus = DatabaseUpdateSaver(database, metrics)

    delayer_factory = DelayerFactory()

    bot = telegram.Bot(config['telegram']['token'])
    messenger = Messenger(bot, database, dus, delayer_factory)

    return config, database, messenger, metrics, dus


def __main__():
    # TODO: use dependency injection tool
    # TODO: inconsistency between factory constructor args and method args: Factory(X).create() vs Factory().create(X)
    config, database, messenger, metrics, dus = init(['./config.json', '/etc/toxic/config.json'])

    sentry_dsn = config['sentry']['dsn']
    if sentry_dsn:
        sentry_sdk.init(sentry_dsn)  # pylint: disable=abstract-class-instantiated
    start_http_server(config['prometheus']['port'], 'localhost')

    joker = JokerFactory().create(config['replies']['joker']['error'])

    server = Server(config['server']['host'], config['server']['port'], database)

    worker_manager = WorkersManager(messenger)
    worker_manager.start([
        ServerWorker(server),
        JokesWorker(joker, database, messenger),
        ReminderWorker(database, messenger),
    ])

    handlers_private = (
        PrivateHandler(config['replies']['private'], database, messenger),
    )

    splitter = SpaceAdjoinSplitter()
    textizer = Textizer(Featurizer(), splitter, metrics)
    chain_factory = ChainFactory(window=2)

    rate_limiter = RateLimiter(
        rate=5,
        per=120,
        reply=config['replies']['rate_limiter'],
        messenger=messenger,
    )

    odesli = Odesli()

    handlers_chats = (
        MusicHandler(odesli, messenger),
        VoiceHandlerFactory().create(config['replies']['voice'], messenger),
        KeywordsHandlerFactory().create(config['replies']['keywords'], messenger),
        SorryHandlerFactory().create(config['replies']['sorry'], messenger),
        StatsHandlerFactory().create(config['replies']['stats'], database, messenger),
        ChainHandlerFactory(chain_factory, textizer, database, messenger).create(),
    )

    commands = (
        CommandDefinition('dump', DumpCommand(database, messenger), True),
        CommandDefinition('stat', StatCommand(database, messenger), False),
        CommandDefinition('joke', JokeCommand(joker, messenger), False),
        CommandDefinition('send', SendCommand(database, messenger), True),
        CommandDefinition('chats', ChatsCommand(database, messenger), True),
        CommandDefinition('voice', VoiceCommand(database, messenger), False),
    )
    handle_manager = HandlersManager(
        handlers_private,
        handlers_chats,
        commands,
        database,
        messenger,
        dus,
        metrics,
        rate_limiter,
    )

    messenger.send_to_admins('Я запустился.')

    messages_total_row = database.query_row('''SELECT count(*) FROM messages''')
    metrics.messages.set(messages_total_row[0])

    # TODO: распутать это всё
    update_id = None
    while True:
        try:
            for update in messenger.bot.get_updates(offset=update_id, timeout=10):
                update_id = update.update_id
                handle_manager.handle_update(update)
                update_id = update.update_id + 1
        except NetworkError as ex:
            logging.error('Network error.', exc_info=ex)
            if isinstance(ex, telegram.error.BadRequest):
                update_id += 1
            time.sleep(1)
        except Unauthorized:  # The user has removed or blocked the bot.
            logging.info('User removed or blocked the bot.')
            update_id += 1
        except Conflict:
            logging.error('Bot is already running somewhere, stopping it.')
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as ex:
            logging.error(
                'Caught an exception while handling an update.',
                exc_info=ex,
            )


if __name__ == '__main__':
    __main__()
