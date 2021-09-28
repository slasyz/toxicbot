import pytest

from toxic.features.odesli import Odesli
from toxic.handlers.music import get_message


@pytest.mark.parametrize(
    ['url', 'message'],
    [
        ('https://open.spotify.com/track/0XauTwcR4Y44zdIS7yV2Jf?si=99dc49931ec14dcc', '''Исполнитель: <b>Он Юн, Александр Смородинов</b>
Трек: <b>Больше нет</b>

<a href="https://geo.music.apple.com/us/album/_/1454338948?i=1454338968&mt=1&app=music&ls=1&at=1000lHKX">Apple Music</a> / <a href="https://open.spotify.com/track/0XauTwcR4Y44zdIS7yV2Jf">Spotify</a> / <a href="https://music.yandex.ru/track/50671259">Яндекс.Музыка</a> / <a href="https://music.youtube.com/watch?v=fDEYWPvq_GQ">YouTube Music</a>'''),
        ('https://music.yandex.ru/album/3491806', '''Исполнитель: <b>Architects</b>

<a href="https://music.yandex.ru/album/3491806">Яндекс.Музыка</a> / <a href="https://music.youtube.com/playlist?list=OLAK5uy_ncfV6gsBjXyer3e3SOaDSdb1_QGvSBbN4">YouTube Music</a>''')
    ]
)
def test_odesli(url, message):
    odesli = Odesli()
    info = odesli.get_info(url)
    assert get_message(info) == message


@pytest.mark.parametrize(
    ['url'],
    [
        ('https://music.yandex.ru/artist/701626',),
        ('https://music.apple.com/ru/artist/architects/182821355?l=en',),
    ],
)
def test_no_info(url):
    odesli = Odesli()
    assert odesli.get_info(url) is None
