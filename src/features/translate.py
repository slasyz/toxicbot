import logging

from translate import Translator


def do(text: str) -> str:
    try:
        translator = Translator("uk", "ru")
        return translator.translate(text)
    except Exception as e:
        logging.error('translate error: %s', e)

    return text
