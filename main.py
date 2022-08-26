#!/usr/bin/env python3
import asyncio
import os
import sys
import time
from dataclasses import dataclass

import aiogram
import asyncpg
from loguru import logger
from pymorphy2 import MorphAnalyzer
from ruwordnet import RuWordNet

from toxic.config import Config
from toxic.db import Database
from toxic.features.chain.chain import ChainFactory
from toxic.features.chain.featurizer import Featurizer
from toxic.features.chain.textizer import Textizer
from toxic.features.emojifier import Emojifier, Russian
from toxic.features.joke import Joker
from toxic.features.music.generator.generator import MusicMessageGenerator
from toxic.features.music.services.boom import Boom
from toxic.features.music.services.collector import MusicInfoCollector
from toxic.features.music.services.odesli import Odesli
from toxic.features.music.services.spotify import Spotify
from toxic.features.taro import Taro
from toxic.handlers import chain
from toxic.features.chain.splitters import SpaceAdjoinSplitter
from toxic.handlers.commands.admin import AdminCommand, AdminChatsCallback, AdminSpotifyAuthCallback, \
    AdminSpotifyAuthCommand, AdminKeyboardClearCallback
from toxic.handlers.commands.hookah import HookahCommand
from toxic.handlers.commands.joke import JokeCommand
from toxic.handlers.commands.chats import ChatsCommand
from toxic.handlers.commands.dump import DumpCommand
from toxic.handlers.commands.music import MusicPlaintextCallback
from toxic.handlers.commands.send import SendCommand
from toxic.handlers.commands.stat import StatCommand, StatsHandler
from toxic.handlers.chat_replies import KeywordsHandler, SorryHandler, PrivateHandler
from toxic.handlers.commands.taro import TaroCommand, TaroSecondCallback, TaroFirstCallback
from toxic.handlers.commands.voice import VoiceCommand
from toxic.handlers.database import DatabaseUpdateSaver
from toxic.handlers.music import MusicHandler
from toxic.handling import CommandDefinition, HandlersManager, CallbackDefinition
from toxic.helpers import log
from toxic.helpers.delayer import DelayerFactory
from toxic.helpers.log import init_sentry
from toxic.helpers.rate_limiter import RateLimiter
from toxic.messenger.messenger import Messenger
from toxic.metrics import Metrics
from toxic.repositories.callback_data import CallbackDataRepository
from toxic.repositories.chats import CachedChatsRepository
from toxic.repositories.messages import MessagesRepository
from toxic.repositories.reminders import RemindersRepository
from toxic.repositories.settings import SettingsRepository
from toxic.repositories.users import UsersRepository
from toxic.workers.jokes import JokesWorker
from toxic.workers.reminders import ReminderWorker
from toxic.workers.spotify_cache import SpotifyCacheWorker
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


def get_resource_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), 'resources', name)


async def init(config_files: list) -> BasicDependencies:
    log.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()  # pylint: disable=no-member

    config = Config.load(config_files)

    return await init_with_config(config)


async def init_with_config(config: Config) -> BasicDependencies:
    database = await Database.connect(
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

    bot = aiogram.Bot(config['telegram']['token'])
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


async def loop(deps: BasicDependencies, handle_manager: HandlersManager):
    # TODO: распутать это всё
    update_id = None
    while True:
        try:
            for update in await deps.messenger.bot.get_updates(offset=update_id, timeout=10):
                update_id = update.update_id
                # TODO: add it to coroutines list
                await handle_manager.handle_update(update)
                update_id = update.update_id + 1
        except aiogram.exceptions.NetworkError as ex:
            logger.opt(exception=ex).error('Network error.')
            await asyncio.sleep(1)
        except aiogram.exceptions.Unauthorized:  # The user has removed or blocked the bot.
            logger.info('User removed or blocked the bot.')
        except aiogram.exceptions.ConflictError as ex:
            logger.opt(exception=ex).error('Bot is already running somewhere, stopping it.')
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)
        except asyncpg.InterfaceError as ex:
            logger.opt(exception=ex).error('Get asyncpg.InterfaceError, stopping.')
            sys.exit(1)
        except Exception as ex:
            logger.opt(exception=ex).error('Caught an exception while handling an update.')


# pylint: disable=too-many-statements
async def __main__():
    deps = await init(['./config.json', '/etc/toxic/config.json'])

    init_sentry(deps.config['sentry']['dsn'])

    reminders_repo = RemindersRepository(deps.database)
    settings_repo = SettingsRepository(deps.database)
    callback_data_repo = CallbackDataRepository(deps.database)

    joker = Joker(deps.config['replies']['joker']['error'])

    spotify_cache_worker = SpotifyCacheWorker(settings_repo)
    spotify = await Spotify.new(deps.config['spotify']['client_id'], deps.config['spotify']['client_secret'], settings_repo, spotify_cache_worker)
    spotify_searcher = spotify.create_searcher()

    music_info_collector = MusicInfoCollector(
        infoers=[Odesli(), Boom()],
        searchers=[spotify_searcher]
    )
    music_formatter = MusicMessageGenerator(music_info_collector, settings_repo, callback_data_repo)

    workers_manager = WorkersManager(deps.messenger)
    workers = [
        JokesWorker(joker, deps.chats_repo, deps.messenger),
        ReminderWorker(reminders_repo, deps.messenger),
        SpotifyCacheWorker(settings_repo),
    ]

    splitter = SpaceAdjoinSplitter()
    textizer = Textizer(Featurizer(), splitter, deps.metrics)
    chain_factory = ChainFactory(window=2)

    rate_limiter = RateLimiter(
        rate=5,
        per=120,
        reply=deps.config['replies']['rate_limiter'],
    )

    taro_dir = get_resource_path('taro')

    wn = RuWordNet()
    morph = MorphAnalyzer()
    russian = Russian(wn, morph)
    emojifier = Emojifier.new(splitter, russian, get_resource_path('emoji_df_result.csv'))

    chain_teaching_handler, chain_flood_handler = await chain.new(chain_factory, textizer, deps.chats_repo, deps.messages_repo, deps.messenger)

    useful_handlers = [
        MusicHandler(music_formatter),
        KeywordsHandler.new(deps.config['replies']['keywords']),
        SorryHandler.new(deps.config['replies']['sorry'], deps.messenger),
        StatsHandler.new(deps.config['replies']['stats'], deps.chats_repo),
        chain_teaching_handler,
    ]
    flood_handlers = [
        chain_flood_handler,
        PrivateHandler(deps.config['replies']['private'], deps.users_repo),
    ]

    commands = [
        CommandDefinition('admin', AdminCommand(spotify, callback_data_repo, settings_repo)),
        CommandDefinition('dump', DumpCommand(deps.messages_repo)),
        CommandDefinition('stat', StatCommand(deps.users_repo, deps.chats_repo)),
        CommandDefinition('joke', JokeCommand(joker)),
        CommandDefinition('send', SendCommand(deps.chats_repo, deps.messenger)),
        CommandDefinition('chats', ChatsCommand(deps.chats_repo)),
        CommandDefinition('voice', VoiceCommand(deps.messages_repo)),
        CommandDefinition('taro', TaroCommand(taro_dir, callback_data_repo)),
        CommandDefinition('spotify', AdminSpotifyAuthCommand(spotify)),
        CommandDefinition('hookah', HookahCommand(emojifier)),
    ]
    callbacks = [
        CallbackDefinition('/taro/first', TaroFirstCallback(taro_dir, deps.messenger, callback_data_repo)),
        CallbackDefinition('/taro/second', TaroSecondCallback(Taro.new(taro_dir), deps.messenger)),
        CallbackDefinition('/admin/chats', AdminChatsCallback(deps.chats_repo)),
        CallbackDefinition('/admin/keyboard/clear', AdminKeyboardClearCallback()),
        CallbackDefinition('/admin/spotify/auth', AdminSpotifyAuthCallback(spotify)),
        CallbackDefinition('/music/plaintext', MusicPlaintextCallback(music_formatter, deps.messenger, deps.config['replies']['music']['error']))
    ]
    handle_manager = HandlersManager(
        [deps.dus],
        callbacks,
        commands,
        useful_handlers,
        flood_handlers,
        deps.users_repo,
        callback_data_repo,
        deps.messenger,
        deps.metrics,
        rate_limiter,
    )

    await deps.messenger.send_to_admins('Я запустился.')

    messages_total_row = await deps.database.query_row('''SELECT count(*) FROM messages''')
    deps.metrics.messages.set(messages_total_row[0])

    await asyncio.gather(
        loop(deps, handle_manager),
        workers_manager.run(workers),
    )


if __name__ == '__main__':
    asyncio.run(__main__())
