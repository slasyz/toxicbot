from src.features.voice import NextUpService
from src.helpers.general import LINK_REGEXP


def test_voice_nextup():
    voice_service = NextUpService()
    link = voice_service.generate_link('тест, проверка')
    assert LINK_REGEXP.match(link)
