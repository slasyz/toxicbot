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
from toxicbot.handlers.database import DatabaseUpdateSaver
from toxicbot.handling import CommandDefinition, HandlersManager
from toxicbot.helpers import log
from toxicbot.messenger import Messenger
from toxicbot.metrics import Metrics
from toxicbot.workers.jokes import JokesWorker
from toxicbot.workers.reminders import ReminderWorker
from toxicbot.workers.server.server import ServerWorker, Server
from toxicbot.workers.worker import WorkersManager


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

    bot = telegram.Bot(config['telegram']['token'])
    messenger = Messenger(bot, database, dus)

    return config, database, messenger, metrics, dus


def __main__():
    # TODO: use dependency injection tool
    # TODO: inconsistency between factory constructor args and method args: Factory(X).create() vs Factory().create(X)
    config, database, messenger, metrics, dus = init(['./config.json', '/etc/toxic/config.json'])

    sentry_dsn = config['sentry']['dsn']
    if sentry_dsn:
        sentry_sdk.init(sentry_dsn)  # pylint: disable=abstract-class-instantiated
    start_http_server(config['prometheus']['port'])

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

    splitter = PunctuationSplitter()
    textizer = Textizer(Featurizer(), splitter, metrics)
    chain_factory = ChainFactory(window=3)

    handlers_chats = (
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
    )
    handle_manager = HandlersManager(
        handlers_private,
        handlers_chats,
        commands,
        database,
        messenger,
        dus,
        metrics,
    )

    messenger.send_to_admins('Я запустился.')

    messages_total_row = database.query_row('''SELECT count(*) FROM messages''')
    metrics.messages.set(messages_total_row[0])

    # TODO: распутать это всё
    update_id = None
    while True:
        try:
            # TODO: messenger.bot bad
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
