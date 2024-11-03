import aiogram
from spotipy import SpotifyOauthError

from toxic.modules.music.services.spotify import Spotify
from toxic.interfaces import CallbackHandler, CommandHandler
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
            [aiogram.types.InlineKeyboardButton(text='📄 Список чатов', callback_data=await self.callback_data_repo.insert_value({'name': '/admin/chats'}))],
            [aiogram.types.InlineKeyboardButton(text='⌨️ Убрать клавиатуру', callback_data=await self.callback_data_repo.insert_value({'name': '/admin/keyboard/clear'}))],
        ]
        if self.spotify:
            spotify_authenticated = False
            try:
                spotify_authenticated = self.spotify.is_authenticated()
            except SpotifyOauthError:
                pass

            if not spotify_authenticated:
                buttons.append(
                    [aiogram.types.InlineKeyboardButton(text='🎶 Spotify 🔑 Authenticate', callback_data=await self.callback_data_repo.insert_value({'name': '/admin/spotify/auth'}))],
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
        async for id, title in self.chats_repo.list():
            response.append(f'{title} — #{id}')

        return TextMessage('\n'.join(response))


class AdminKeyboardClearCallback(CallbackHandler):
    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, callback: aiogram.types.CallbackQuery, message: aiogram.types.Message, args: dict) -> Message | CallbackReply | None:
        return TextMessage('Ок.', markup=aiogram.types.ReplyKeyboardRemove())
