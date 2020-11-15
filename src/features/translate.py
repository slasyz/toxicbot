import logging

from translate import Translator


def do(text: str, lang_from: str = 'ru', lang_to: str = 'uk') -> str:
    try:
        translator = Translator(lang_to, lang_from)
        return translator.translate(text)
    except Exception as ex:
        logging.error('translate error: %s', ex)

    return text
