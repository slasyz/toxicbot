import aiogram

from toxic.interfaces import CommandHandler
from toxic.messenger.message import Message
from toxic.repository import Repository


class ChatsCommand(CommandHandler):
    def __init__(self, repo: Repository):
        self.repo = repo

    @staticmethod
    def is_admins_only() -> bool:
        return True

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        response = []
        async for id, title in self.repo.list_chats():
            response.append(f'{title} — #{id}')

        return '\n'.join(response)
