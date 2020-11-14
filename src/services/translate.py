import logging as pylogging

from translate import Translator


def do(text: str) -> str:
    try:
        translator = Translator("uk", "ru")
        return translator.translate(text)
    except Exception as e:
        pylogging.error('translate error: %s', e)

    return text
