#!/usr/bin/env python3
import os
import sys
import time
import logging
from dataclasses import dataclass

import sentry_sdk
import telegram
from telegram.error import NetworkError, Unauthorized, Conflict

from toxic.config import Config
from toxic.db import Database
from toxic.features.chain.chain import ChainFactory
from toxic.features.chain.featurizer import Featurizer
from toxic.features.chain.textizer import Textizer
from toxic.features.joke import Joker
from toxic.features.odesli import Odesli
from toxic.features.taro import Taro
from toxic.handlers.chain import ChainHandler
from toxic.features.chain.splitters import SpaceAdjoinSplitter
from toxic.handlers.commands.joke import JokeCommand
from toxic.handlers.commands.chats import ChatsCommand
from toxic.handlers.commands.dump import DumpCommand
from toxic.handlers.commands.send import SendCommand
from toxic.handlers.commands.stat import StatCommand, StatsHandler
from toxic.handlers.chat_replies import PrivateHandler, KeywordsHandler, SorryHandler
from toxic.handlers.commands.taro import TaroCommand, TaroSecondCallbackHandler, TaroFirstCallbackHandler
from toxic.handlers.commands.voice import VoiceCommand
from toxic.handlers.database import DatabaseUpdateSaver
from toxic.handlers.music import MusicHandler
from toxic.handling import CommandDefinition, HandlersManager, CallbackDefinition
from toxic.helpers import log
from toxic.helpers.delayer import DelayerFactory
from toxic.helpers.rate_limiter import RateLimiter
from toxic.messenger.messenger import Messenger
from toxic.metrics import Metrics
from toxic.repositories.chats import CachedChatsRepository
from toxic.repositories.messages import MessagesRepository
from toxic.repositories.reminders import RemindersRepository
from toxic.repositories.users import UsersRepository
from toxic.workers.jokes import JokesWorker
from toxic.workers.reminders import ReminderWorker
from toxic.workers.worker import WorkersManager


@dataclass
class BasicDependencies:
    config: Config
    database: Database
    chats_repo: CachedChatsRepository
    messages_repo: MessagesRepository
    users_repo: UsersRepository
    messenger: Messenger
    metrics: Metrics
    dus: DatabaseUpdateSaver

    def __iter__(self):
        return iter((self.config, self.database, self.chats_repo, self.messenger, self.metrics, self.dus))


def get_resource_subdir(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), 'resources', name)


def init(config_files: list) -> BasicDependencies:
    log.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()  # pylint: disable=no-member

    config = Config.load(config_files)

    database = Database.connect(
        config['database']['host'],
        config['database']['port'],
        config['database']['name'],
        config['database']['user'],
        config['database']['pass'],
    )

    chats_repo = CachedChatsRepository(database)
    messages_repo = MessagesRepository(database)
    users_repo = UsersRepository(database)

    metrics = Metrics()

    dus = DatabaseUpdateSaver(database, metrics)

    delayer_factory = DelayerFactory()

    bot = telegram.Bot(config['telegram']['token'])
    messenger = Messenger(bot, chats_repo, users_repo, dus, delayer_factory)

    return BasicDependencies(
        config,
        database,
        chats_repo,
        messages_repo,
        users_repo,
        messenger,
        metrics,
        dus,
    )


def init_sentry(config: Config):
    sentry_dsn = config['sentry']['dsn']
    if sentry_dsn:
        sentry_sdk.init(sentry_dsn)  # pylint: disable=abstract-class-instantiated


def __main__():
    deps = init(['./config.json', '/etc/toxic/config.json'])

    init_sentry(deps.config)

    reminders_repo = RemindersRepository(deps.database)

    joker = Joker(deps.config['replies']['joker']['error'])

    worker_manager = WorkersManager(deps.messenger)
    worker_manager.start([
        JokesWorker(joker, deps.chats_repo, deps.messenger),
        ReminderWorker(reminders_repo, deps.messenger),
    ])

    handlers_private = (
        PrivateHandler(deps.config['replies']['private'], deps.users_repo, deps.messenger),
    )

    splitter = SpaceAdjoinSplitter()
    textizer = Textizer(Featurizer(), splitter, deps.metrics)
    chain_factory = ChainFactory(window=2)

    rate_limiter = RateLimiter(
        rate=5,
        per=120,
        reply=deps.config['replies']['rate_limiter'],
        messenger=deps.messenger,
    )

    taro_dir = get_resource_subdir('taro')

    handlers_chats = (
        MusicHandler(Odesli(), deps.messenger),
        KeywordsHandler.new(deps.config['replies']['keywords'], deps.messenger),
        SorryHandler.new(deps.config['replies']['sorry'], deps.messenger),
        StatsHandler.new(deps.config['replies']['stats'], deps.chats_repo, deps.messenger),
        ChainHandler.new(chain_factory, textizer, deps.chats_repo, deps.messages_repo, deps.messenger),
    )

    commands = (
        CommandDefinition('dump', DumpCommand(deps.messages_repo, deps.messenger), True),
        CommandDefinition('stat', StatCommand(deps.users_repo, deps.chats_repo, deps.messenger), False),
        CommandDefinition('joke', JokeCommand(joker, deps.messenger), False),
        CommandDefinition('send', SendCommand(deps.chats_repo, deps.messenger), True),
        CommandDefinition('chats', ChatsCommand(deps.chats_repo, deps.messenger), True),
        CommandDefinition('voice', VoiceCommand(deps.messages_repo, deps.messenger), False),
        CommandDefinition('taro', TaroCommand(taro_dir, deps.messenger), False),
    )
    callbacks = (
        CallbackDefinition('taro_first', TaroFirstCallbackHandler(taro_dir, deps.messenger)),
        CallbackDefinition('taro_second', TaroSecondCallbackHandler(Taro.new(taro_dir), deps.messenger)),
    )
    handle_manager = HandlersManager(
        handlers_private,
        handlers_chats,
        commands,
        callbacks,
        deps.users_repo,
        deps.messenger,
        deps.dus,
        deps.metrics,
        rate_limiter,
    )

    deps.messenger.send_to_admins('Я запустился.')

    messages_total_row = deps.database.query_row('''SELECT count(*) FROM messages''')
    deps.metrics.messages.set(messages_total_row[0])

    # TODO: распутать это всё
    update_id = None
    while True:
        try:
            for update in deps.messenger.bot.get_updates(offset=update_id, timeout=10):
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
