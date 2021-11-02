import pytest

from toxic.features.music.odesli import Odesli
from toxic.handlers.music import get_message_and_buttons


# TODO: use more services, for example https://songwhip.com/faq and direct APIs


@pytest.mark.parametrize(
    ['url', 'message', 'services'],
    [
        (
            'https://open.spotify.com/track/0XauTwcR4Y44zdIS7yV2Jf?si=99dc49931ec14dcc',
            '''Исполнитель: <b>Он Юн, Александр Смородинов</b>
Трек: <b>Больше нет</b>''',
            (
                ('Apple Music', 'https://geo.music.apple.com/us/album/_/1454338948?i=1454338968&mt=1&app=music&ls=1&at=1000lHKX'),
                ('Spotify', 'https://open.spotify.com/track/0XauTwcR4Y44zdIS7yV2Jf'),
                ('Яндекс.Музыка', 'https://music.yandex.ru/track/50671259'),
                ('YouTube', 'https://youtube.com/watch?v=fDEYWPvq_GQ'),
            )
        ),
        (
            'https://music.yandex.ru/album/3491806',
            '''Исполнитель: <b>Architects</b>
Альбом: <b>All Our Gods Have Abandoned Us</b>''',
            (
                ('Apple Music', 'https://music.yandex.ru/album/3491806'),
                ('Spotify', ''),
                ('Яндекс.Музыка', ''),
                ('YouTube', 'https://youtube.com/playlist?list=OLAK5uy_ncfV6gsBjXyer3e3SOaDSdb1_QGvSBbN4'),
            )
        ),
        (
            'https://open.spotify.com/album/7qEap2Ip3FeBPEPLr9YaJc?si=yyCIl_QOS3OkdWM4crEUaw&dl_branch=1',
            '''Исполнитель: <b>Aikko</b>
Альбом: <b>Тёмные делишки</b>''',
            (
                ('Apple Music', 'https://geo.music.apple.com/us/album/_/1582455767?mt=1&app=music&ls=1&at=1000lHKX'),
                ('Spotify', 'https://open.spotify.com/album/7qEap2Ip3FeBPEPLr9YaJc'),
                ('Яндекс.Музыка', 'https://music.yandex.ru/album/17877728'),
                ('YouTube', 'https://youtube.com/playlist?list=OLAK5uy_mNkJ0lQooA_ZOEo3cK0gUXWWVv1vHBiYo'),
            )
        )
    ]
)
def test_odesli(url, message, services):
    odesli = Odesli()
    info = odesli.get_info(url)
    message_actual, _, _ = get_message_and_buttons(info)
    assert message_actual == message


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
