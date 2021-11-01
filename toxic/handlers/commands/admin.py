import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from toxic.features.spotify import Spotify
from toxic.handlers.commands.command import Command
from toxic.handlers.handler import CallbackHandler
from toxic.messenger.message import TextMessage
from toxic.messenger.messenger import Messenger
from toxic.repositories.callback_data import CallbackDataRepository
from toxic.repositories.chats import ChatsRepository
from toxic.repositories.settings import SettingsRepository


class AdminCommand(Command):
    def __init__(self, messenger: Messenger, spotify: Spotify, callback_data_repo: CallbackDataRepository):
        self.messenger = messenger
        self.spotify = spotify
        self.callback_data_repo = callback_data_repo

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        buttons = [
            [InlineKeyboardButton('Список чатов', callback_data=self.callback_data_repo.insert_value({'name': '/admin/chats'}))],
        ]
        if not self.spotify.is_authenticated():
            buttons.append(
                [InlineKeyboardButton('Spotify Authenticate', callback_data=self.callback_data_repo.insert_value({'name': '/admin/spotify/auth'}))],
            )
        buttons.append([
            InlineKeyboardButton('Spotify Set Device', callback_data=self.callback_data_repo.insert_value({'name': '/admin/spotify/set_device'})),
            InlineKeyboardButton('Spotify Disable', callback_data=self.callback_data_repo.insert_value({'name': '/admin/spotify/disable'})),
        ])

        self.messenger.reply(message, TextMessage(
            text='Доступные команды',
            markup=InlineKeyboardMarkup(buttons),
        ))


class AdminChatsHandler(CallbackHandler):
    def __init__(self, chats_repo: ChatsRepository, messenger: Messenger):
        self.chats_repo = chats_repo
        self.messenger = messenger

    def handle(self, callback: telegram.CallbackQuery, _args: dict):
        message = callback.message
        if message is None:
            return

        response = []
        for id, title in self.chats_repo.list():
            response.append(f'{title} — #{id}')

        self.messenger.send(message.chat_id, '\n'.join(response))


class AdminSpotifyAuth(CallbackHandler):
    def __init__(self, spotify: Spotify, messenger: Messenger):
        self.spotify = spotify
        self.messenger = messenger

    def handle(self, callback: telegram.CallbackQuery, _args: dict):
        if self.spotify.is_authenticated():
            callback.answer('Уже авторизован.')
            return

        message = callback.message
        if message is None:
            return

        self.messenger.send(message.chat_id, TextMessage(
            text='Перейди по ссылке, чтобы авторизоваться.\n\nА потом пришли /spotify URL, где URL — это то, куда перенаправила страница авторизации.',
            markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('👉', self.spotify.get_auth_url()),
            ]])
        ))


class AdminSpotifyAuthCommand(Command):
    def __init__(self, messenger: Messenger, spotify: Spotify):
        self.messenger = messenger
        self.spotify = spotify

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        if len(args) != 2:
            self.messenger.reply(message, 'Нужно писать так: /spotify URL')
            return

        url = args[1]
        self.spotify.authenticate(url)
        self.messenger.reply(message, 'Успешно авторизован.')


class AdminSpotifySetDevice(CallbackHandler):
    def __init__(self, settings_repo: SettingsRepository, callback_data_repo: CallbackDataRepository, messenger: Messenger, spotify: Spotify):
        self.settings_repo = settings_repo
        self.callback_data_repo = callback_data_repo
        self.messenger = messenger
        self.spotify = spotify

    def handle(self, callback: telegram.CallbackQuery, args: dict):
        message = callback.message
        if message is None:
            return

        device_id = args.get('device_id')
        if device_id is None:
            devices = self.spotify.get_devices()
            buttons = []
            for device in devices:
                print(device.device_id)
                buttons.append([InlineKeyboardButton(
                    device.name,
                    callback_data=self.callback_data_repo.insert_value({'name': '/admin/spotify/set_device', 'device_id': device.device_id}),
                )])
            self.messenger.send(message.chat_id, TextMessage(
                'Выбери устройство:',
                markup=InlineKeyboardMarkup(buttons)
            ))
            return

        # TODO: validate device id
        self.settings_repo.spotify_set_device(device_id)
        self.messenger.send(message.chat_id, 'Устройство установлено в Spotify.')


class AdminSpotifyDisable(CallbackHandler):
    def __init__(self, settings_repo: SettingsRepository, messenger: Messenger):
        self.settings_repo = settings_repo
        self.messenger = messenger

    def handle(self, callback: telegram.CallbackQuery, args: dict):
        message = callback.message
        if message is None:
            return

        self.settings_repo.spotify_disable()
        self.messenger.send(message.chat_id, 'Отключил Spotify.')
