import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from toxic.features.music.spotify import Spotify
from toxic.handlers.handler import CallbackHandler, CommandHandler
from toxic.messenger.message import TextMessage
from toxic.messenger.messenger import Messenger
from toxic.repositories.callback_data import CallbackDataRepository
from toxic.repositories.chats import ChatsRepository
from toxic.repositories.settings import SettingsRepository


class AdminCommand(CommandHandler):
    def __init__(self, messenger: Messenger, spotify: Spotify, callback_data_repo: CallbackDataRepository, settings_repo: SettingsRepository):
        self.messenger = messenger
        self.spotify = spotify
        self.callback_data_repo = callback_data_repo
        self.settings_repo = settings_repo

    @staticmethod
    def is_admins_only() -> bool:
        return True

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        buttons = [
            [InlineKeyboardButton('📄 Список чатов', callback_data=self.callback_data_repo.insert_value({'name': '/admin/chats'}))],
        ]
        if not self.spotify.is_authenticated():
            buttons.append(
                [InlineKeyboardButton('🎶 Spotify 🔑 Authenticate', callback_data=self.callback_data_repo.insert_value({'name': '/admin/spotify/auth'}))],
            )

        buttons_spotify = [InlineKeyboardButton('🎶 Spotify 🎧 Set Device', callback_data=self.callback_data_repo.insert_value({'name': '/admin/spotify/set_device'}))]
        if self.settings_repo.is_spotify_enabled():
            buttons_spotify.append(InlineKeyboardButton('🎶 Spotify 🔇 Disable', callback_data=self.callback_data_repo.insert_value({'name': '/admin/spotify/state', 'action': 'disable'})))
        else:
            buttons_spotify.append(InlineKeyboardButton('🎶 Spotify 🔈 Enable', callback_data=self.callback_data_repo.insert_value({'name': '/admin/spotify/state', 'action': 'enable'})))
        buttons.append(buttons_spotify)

        self.messenger.reply(message, TextMessage(
            text='Доступные команды',
            markup=InlineKeyboardMarkup(buttons),
        ))


class AdminChatsCallback(CallbackHandler):
    def __init__(self, chats_repo: ChatsRepository, messenger: Messenger):
        self.chats_repo = chats_repo
        self.messenger = messenger

    @staticmethod
    def is_admins_only() -> bool:
        return True

    def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict):
        response = []
        for id, title in self.chats_repo.list():
            response.append(f'{title} — #{id}')

        self.messenger.send(message.chat_id, '\n'.join(response))


class AdminSpotifyAuthCallback(CallbackHandler):
    def __init__(self, spotify: Spotify, messenger: Messenger):
        self.spotify = spotify
        self.messenger = messenger

    @staticmethod
    def is_admins_only() -> bool:
        return True

    def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict):
        if self.spotify.is_authenticated():
            self.messenger.reply_callback(callback, 'Уже авторизован.', show_alert=True)
            return

        self.messenger.send(message.chat_id, TextMessage(
            text='Перейди по ссылке, чтобы авторизоваться.\n\nА потом пришли /spotify URL, где URL — это то, куда перенаправила страница авторизации.',
            markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('👉', self.spotify.get_auth_url()),
            ]])
        ))


class AdminSpotifyAuthCommand(CommandHandler):
    def __init__(self, messenger: Messenger, spotify: Spotify):
        self.messenger = messenger
        self.spotify = spotify

    @staticmethod
    def is_admins_only() -> bool:
        return True

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        if len(args) != 2:
            self.messenger.reply(message, 'Нужно писать так: /spotify URL')
            return

        url = args[1]
        self.spotify.authenticate(url)
        self.messenger.reply(message, 'Успешно авторизован.')


class AdminSpotifySetDeviceCallback(CallbackHandler):
    def __init__(self, settings_repo: SettingsRepository, callback_data_repo: CallbackDataRepository, messenger: Messenger, spotify: Spotify):
        self.settings_repo = settings_repo
        self.callback_data_repo = callback_data_repo
        self.messenger = messenger
        self.spotify = spotify

    @staticmethod
    def is_admins_only() -> bool:
        return True

    def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict):
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


class AdminSpotifyStateCallback(CallbackHandler):
    def __init__(self, settings_repo: SettingsRepository, messenger: Messenger):
        self.settings_repo = settings_repo
        self.messenger = messenger

    @staticmethod
    def is_admins_only() -> bool:
        return True

    def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict):
        action = args.get('action')
        if action is None:
            return

        if action == 'enable':
            self.settings_repo.spotify_enable()
            self.messenger.send(message.chat_id, 'Включил Spotify.')
        else:
            self.settings_repo.spotify_disable()
            self.messenger.send(message.chat_id, 'Отключил Spotify.')
