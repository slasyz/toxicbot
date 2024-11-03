import os

import aiogram
from loguru import logger

from toxic.interfaces import CommandHandler, CallbackHandler
from toxic.modules.taro.content import Taro, CardData
from toxic.messenger.message import TextMessage, PhotoMessage, Message, CallbackReply
from toxic.messenger.messenger import Messenger
from toxic.repository import Repository


class TaroCommand(CommandHandler):
    def __init__(self, res_dir: str, repo: Repository):
        self.res_dir = res_dir
        self.repo = repo

    async def handle(self, text: str, message: aiogram.types.Message, args: list[str]) -> str | list[Message] | None:
        goals = ['general', 'love', 'question', 'daily', 'advice']
        buttons = []
        for goal in goals:
            buttons.append([
                aiogram.types.InlineKeyboardButton(
                    text=GOALS_EMOJI[goal] + ' ' + GOALS[goal],
                    callback_data=await self.repo.insert_callback_value({'name': '/taro/first', 'goal': goal}),
                ),
            ])
        return [TextMessage(
            text='🧙 🌟 Что хотим получить от Вселенной? 🪐 🪄',
            markup=aiogram.types.InlineKeyboardMarkup(inline_keyboard=buttons),
        )]


GOALS_EMOJI = {
    'general': '🃏',
    'love': '❤️',
    'question': '❓',
    'daily': '🗓',
    'advice': '🤲',
}
GOALS = {
    'general': 'общее предсказание',
    'love': 'предсказание в любви',
    'question': 'ответ на вопрос',
    'daily': 'значение дня',
    'advice': 'совет',
}


def get_description_by_goal(card: CardData, goal: str) -> str:
    if goal == 'general':
        return card.general_forwards
    if goal == 'love':
        return card.love_forwards
    if goal == 'daily':
        return card.daily
    if goal == 'advice':
        return card.advice
    return card.general_forwards


def get_mention(user: aiogram.types.User):
    if user.username != '':
        return f'<a href="tg://user?id={user.id}">@{user.username}</a>'
    return f'<a href="tg://user?id={user.id}">{user.first_name}</a>'


class TaroFirstCallback(CallbackHandler):
    def __init__(self, res_dir: str, messenger: Messenger, repo: Repository):
        self.res_dir = res_dir
        self.messenger = messenger
        self.repo = repo

    async def handle(self, callback: aiogram.types.CallbackQuery, message: aiogram.types.Message, args: dict) -> Message | CallbackReply | None:
        with open(os.path.join(self.res_dir, 'back.jpg'), 'rb') as f:
            photo = f.read()

        goal = args.get('goal', '')
        mention = get_mention(callback.from_user)

        await self.messenger.send(message.chat.id, PhotoMessage(
            photo=photo,
            text=f'{mention}, выбери карту, чтобы получить {GOALS.get(goal, "general")}.',
            is_html=True,
            markup=aiogram.types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    aiogram.types.InlineKeyboardButton(text='1️⃣', callback_data=await self.repo.insert_callback_value({'name': '/taro/second', 'goal': goal})),
                    aiogram.types.InlineKeyboardButton(text='2️⃣', callback_data=await self.repo.insert_callback_value({'name': '/taro/second', 'goal': goal})),
                ],
                [
                    aiogram.types.InlineKeyboardButton(text='3️⃣', callback_data=await self.repo.insert_callback_value({'name': '/taro/second', 'goal': goal})),
                    aiogram.types.InlineKeyboardButton(text='4️⃣', callback_data=await self.repo.insert_callback_value({'name': '/taro/second', 'goal': goal})),
                ]
            ])
        ))
        await self.messenger.delete_message(message.chat.id, message.message_id)
        return None


class TaroSecondCallback(CallbackHandler):
    def __init__(self, taro: Taro, messenger: Messenger):
        self.taro = taro
        self.messenger = messenger

    async def handle(self, callback: aiogram.types.CallbackQuery, message: aiogram.types.Message, args: dict) -> Message | CallbackReply | None:
        card = self.taro.get_random_card()

        logger.info('Handling taro callback.', args=args)

        goal = args.get('goal', '')
        description = get_description_by_goal(card.data, goal)

        mention = get_mention(callback.from_user)

        await self.messenger.send(message.chat.id, PhotoMessage(
            photo=card.image,
            text=f'''{mention}, тебе выпала карта <b>{card.data.name}</b>\n\n{description}''',
            is_html=True,
        ))
        await self.messenger.delete_message(message.chat.id, message.message_id)
        return None
