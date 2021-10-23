from loguru import logger
from translate import Translator


def do(text: str, lang_from: str = 'ru', lang_to: str = 'uk') -> str:
    try:
        translator = Translator(lang_to, lang_from)
        return translator.translate(text)
    except Exception as ex:
        logger.opt(exception=ex).error('Translate error.')

    return text
