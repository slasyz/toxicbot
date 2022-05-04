import aiogram

from toxic.features.music.services.spotify import Spotify
from toxic.handlers.handler import CallbackHandler, CommandHandler
from toxic.messenger.message import TextMessage, Message, CallbackReply
from toxic.repositories.callback_data import CallbackDataRepository
from toxic.repositories.chats import ChatsRepository
from toxic.repositories.settings import SettingsRepository


class AdminCommand(CommandHandler):
    def __init__(self, spotify: Spotify | None, callback_data_repo: CallbackDataRepository, settings_repo: SettingsRepository):
        self.spotify = spotify
        self.callback_data_repo = callback_data_repo
        self.settings_repo = settings_repo

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        buttons = [
            [aiogram.types.InlineKeyboardButton('📄 Список чатов', callback_data=self.callback_data_repo.insert_value({'name': '/admin/chats'}))],
        ]
        if self.spotify and not self.spotify.is_authenticated():
            buttons.append(
                [aiogram.types.InlineKeyboardButton('🎶 Spotify 🔑 Authenticate', callback_data=self.callback_data_repo.insert_value({'name': '/admin/spotify/auth'}))],
            )

        return [TextMessage(
            text='Доступные команды',
            markup=aiogram.types.InlineKeyboardMarkup(inline_keyboard=buttons),
        )]


class AdminChatsCallback(CallbackHandler):
    def __init__(self, chats_repo: ChatsRepository):
        self.chats_repo = chats_repo

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, callback: aiogram.types.CallbackQuery, message: aiogram.types.Message, args: dict) -> Message | CallbackReply | None:
        response = []
        for id, title in self.chats_repo.list():
            response.append(f'{title} — #{id}')

        return TextMessage('\n'.join(response))


class AdminSpotifyAuthCallback(CallbackHandler):
    def __init__(self, spotify: Spotify):
        self.spotify = spotify

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, callback: aiogram.types.CallbackQuery, message: aiogram.types.Message, args: dict) -> Message | CallbackReply | None:
        if self.spotify.is_authenticated():
            return CallbackReply('Уже авторизован.', show_alert=True)

        return TextMessage(
            text='Перейди по ссылке, чтобы авторизоваться.\n\nА потом пришли /spotify URL, где URL — это то, куда перенаправила страница авторизации.',
            markup=aiogram.types.InlineKeyboardMarkup(inline_keyboard=[[
                aiogram.types.InlineKeyboardButton('👉', self.spotify.get_auth_url()),
            ]])
        )


class AdminSpotifyAuthCommand(CommandHandler):
    def __init__(self, spotify: Spotify):
        self.spotify = spotify

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        if len(args) != 2:
            return 'Нужно писать так: /spotify URL'

        url = args[1]
        self.spotify.authenticate(url)
        return 'Успешно авторизован.'
