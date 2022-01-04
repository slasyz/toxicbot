import pytest

from toxic.features.music.services.boom import Boom
from toxic.features.music.services.structs import Info, Type, Service


@pytest.mark.parametrize(
    ['url', 'test_func'],
    [
        (
            'https://share.boom.ru/track/f0bd036dab646273eb22e93a03227165/?share_auth=026fcd42eda5b460b9831a617ff2e01a10651e6c1a00631872',
            lambda data: data['tracksStore']['itemShare']['name'] == 'Холода',
        ),
        (
            'https://share.boom.ru/album/6470022/?share_auth=025425f555c2c834c6811a61816080',
            lambda data: data['albumsStore']['itemShare']['name'] == 'Дом с нормальными явлениями',
        ),
        (
            'https://share.boom.ru/artist/66721/?share_auth=02b256a0b5e773bfad811a61816080',
            lambda data: data['artistsStore']['itemShare']['name'] == 'Скриптонит',
        )
    ]
)
def test_get_json(url, test_func):
    boom = Boom()
    data = boom._get_json(url)
    assert test_func(data)


@pytest.mark.parametrize(
    ['url', 'expected_info'],
    [
        (
            'https://share.boom.ru/track/f0bd036dab646273eb22e93a03227165/?share_auth=026fcd42eda5b460b9831a617ff2e01a10651e6c1a00631872',
            Info(
                type=Type.SONG,
                artist_name='Грязь',
                title='Холода',
                links={Service.BOOM: 'https://share.boom.ru/track/f0bd036dab646273eb22e93a03227165/?share_auth=026fcd42eda5b460b9831a617ff2e01a10651e6c1a00631872'}
            )
        ),
        (
            'https://share.boom.ru/album/6470022/?share_auth=025425f555c2c834c6811a61816080',
            Info(
                type=Type.ALBUM,
                artist_name='Скриптонит',
                title='Дом с нормальными явлениями',
                links={Service.BOOM: 'https://share.boom.ru/album/6470022/?share_auth=025425f555c2c834c6811a61816080'}
            ),
        ),
        (
            'https://share.boom.ru/artist/66721/?share_auth=02b256a0b5e773bfad811a61816080',
            Info(
                type=Type.ARTIST,
                artist_name='Скриптонит',
                links={Service.BOOM: 'https://share.boom.ru/artist/66721/?share_auth=02b256a0b5e773bfad811a61816080'}
            ),
        )
    ]
)
def test_get_info(url: str, expected_info: Info):
    boom = Boom()
    info = boom.get_info(url)
    assert info == expected_info
