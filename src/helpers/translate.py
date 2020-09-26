from translate import Translator

import logging as pylogging


def do(text: str) -> str:
    try:
        translator = Translator("uk", "ru")
        return translator.translate(text)
    except Exception as e:
        pylogging.error(f'translate error: {e}')

    return text
