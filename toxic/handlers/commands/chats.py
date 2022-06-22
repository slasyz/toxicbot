import aiogram

from toxic.handlers.handler import CommandHandler
from toxic.messenger.message import Message
from toxic.repositories.chats import ChatsRepository


class ChatsCommand(CommandHandler):
    def __init__(self, chats_repo: ChatsRepository):
        self.chats_repo = chats_repo

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        response = []
        async for id, title in self.chats_repo.list():
            response.append(f'{title} — #{id}')

        return '\n'.join(response)
