import os

import telegram
from loguru import logger
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, User

from toxic.features.taro import Taro, CardData
from toxic.handlers.handler import CallbackHandler, CommandHandler
from toxic.messenger.message import TextMessage, PhotoMessage
from toxic.messenger.messenger import Messenger
from toxic.repositories.callback_data import CallbackDataRepository


class TaroCommand(CommandHandler):
    def __init__(self, res_dir: str, messenger: Messenger, callback_data_repo: CallbackDataRepository):
        self.res_dir = res_dir
        self.messenger = messenger
        self.callback_data_repo = callback_data_repo

    def handle(self, text: str, message: telegram.Message, args: list[str]):
        goals = ['general', 'love', 'question', 'daily', 'advice']
        buttons = []
        for goal in goals:
            buttons.append([
                InlineKeyboardButton(
                    GOALS_EMOJI[goal] + ' ' + GOALS[goal],
                    callback_data=self.callback_data_repo.insert_value({'name': '/taro/first', 'goal': goal}),
                ),
            ])
        self.messenger.reply(message, TextMessage(
            text='🧙 🌟 Что хотим получить от Вселенной? 🪐 🪄',
            markup=InlineKeyboardMarkup(buttons),
        ))


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


def get_mention(user: User):
    if user.username != '':
        return '<a href="tg://user?id={}">@{}</a>'.format(user.id, user.username)
    return '<a href="tg://user?id={}">{}</a>'.format(user.id, user.first_name)


class TaroFirstCallback(CallbackHandler):
    def __init__(self, res_dir: str, messenger: Messenger, callback_data_repo: CallbackDataRepository):
        self.res_dir = res_dir
        self.messenger = messenger
        self.callback_data_repo = callback_data_repo

    def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict):
        with open(os.path.join(self.res_dir, 'back.jpg'), 'rb') as f:
            photo = f.read()

        goal = args.get('goal', '')
        mention = get_mention(callback.from_user)

        self.messenger.send(message.chat_id, PhotoMessage(
            photo=photo,
            text='{}, выбери карту, чтобы получить {}.'.format(mention, GOALS.get(goal, 'general')),
            is_html=True,
            markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton('1️⃣', callback_data=self.callback_data_repo.insert_value({'name': 'taro_second', 'goal': goal})),
                    InlineKeyboardButton('2️⃣', callback_data=self.callback_data_repo.insert_value({'name': 'taro_second', 'goal': goal})),
                ],
                [
                    InlineKeyboardButton('3️⃣', callback_data=self.callback_data_repo.insert_value({'name': 'taro_second', 'goal': goal})),
                    InlineKeyboardButton('4️⃣', callback_data=self.callback_data_repo.insert_value({'name': 'taro_second', 'goal': goal})),
                ]
            ])
        ))
        self.messenger.delete_message(message.chat_id, message.message_id)


class TaroSecondCallback(CallbackHandler):
    def __init__(self, taro: Taro, messenger: Messenger):
        self.taro = taro
        self.messenger = messenger

    def handle(self, callback: telegram.CallbackQuery, message: telegram.Message, args: dict):
        card = self.taro.get_random_card()

        logger.info('Handling taro callback: {}.', args)

        goal = args.get('goal', '')
        description = get_description_by_goal(card.data, goal)

        mention = get_mention(callback.from_user)

        self.messenger.send(message.chat_id, PhotoMessage(
            photo=card.image,
            text=f'''{mention}, тебе выпала карта <b>{card.data.name}</b>\n\n{description}''',
            is_html=True,
        ))
        self.messenger.delete_message(message.chat_id, message.message_id)
