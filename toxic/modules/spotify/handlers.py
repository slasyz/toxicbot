import aiogram

from toxic.interfaces import CallbackHandler, CommandHandler
from toxic.modules.music.services.spotify import Spotify
from toxic.messenger.message import TextMessage, Message, CallbackReply


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
