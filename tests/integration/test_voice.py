from src.features.voice import NextUpService
from src.helpers.general import LINK_REGEXP


def test_voice_nextup():
    voice_service = NextUpService()
    link = voice_service.generate_link('тест, проверка')
    assert LINK_REGEXP.match(link)


def __main__():
    import os  # pylint: disable=import-outside-toplevel
    import time  # pylint: disable=import-outside-toplevel

    import telegram  # pylint: disable=import-outside-toplevel

    from src import db  # pylint: disable=import-outside-toplevel
    from src.helpers import general  # pylint: disable=import-outside-toplevel
    from src.helpers.message import VoiceMessage  # pylint: disable=import-outside-toplevel
    from src import config  # pylint: disable=import-outside-toplevel
    from src.helpers import log  # pylint: disable=import-outside-toplevel

    log.init()
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()

    config.load('../../config.json')
    db.connect()

    general.bot = telegram.Bot(config.c['telegram']['token'])

    general.send(-328967401, VoiceMessage('приветик, чикуля-красотка, чем занимаешься?'))


if __name__ == '__main__':
    __main__()
