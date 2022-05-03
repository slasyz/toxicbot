import pytest

from toxic.features.music.services.odesli import Odesli


# TODO: use more services, for example https://songwhip.com/faq and direct APIs
from toxic.features.music.services.structs import Info, Type, Service


@pytest.mark.parametrize(
    ['url', 'expected'],
    [
        (
            'https://open.spotify.com/track/0XauTwcR4Y44zdIS7yV2Jf?si=99dc49931ec14dcc',
            Info(
                type=Type.SONG,
                artist_name='Александр Смородинов, Он Юн',
                title='Больше нет',
                links={
                    Service.APPLE_MUSIC: 'https://geo.music.apple.com/us/album/_/1454338948',
                    Service.SPOTIFY: 'https://open.spotify.com/track/0XauTwcR4Y44zdIS7yV2Jf',
                    Service.YANDEX: 'https://music.yandex.ru/track/50671259',
                    Service.YOUTUBE: 'https://www.youtube.com/watch?v=fDEYWPvq_GQ',
                },
                thumbnail_url='https://m.media-amazon.com/images/I/61h-+dzapJL.jpg',
            )
        ),

        (
            'https://music.yandex.ru/album/3491806',
            Info(
                type=Type.ALBUM,
                artist_name='Architects',
                title='All Our Gods Have Abandoned Us',
                links={
                    Service.YANDEX: 'https://music.yandex.ru/album/3491806',
                    Service.YOUTUBE: 'https://www.youtube.com/playlist?list=OLAK5uy_lbCwtJN6NJu_UEQrz2S_XSdF2COD3mq0w'
                },
                thumbnail_url='https://avatars.yandex.net/get-music-content/38044/b41875c8.a.3491806-2/600x600',
            )
        ),

        (
            'https://open.spotify.com/album/7qEap2Ip3FeBPEPLr9YaJc?si=yyCIl_QOS3OkdWM4crEUaw&dl_branch=1',
            Info(
                type=Type.ALBUM,
                artist_name='Aikko',
                title='Тёмные делишки',
                links={
                    Service.APPLE_MUSIC: 'https://geo.music.apple.com/us/album/_/1582455767',
                    Service.SPOTIFY: 'https://open.spotify.com/album/7qEap2Ip3FeBPEPLr9YaJc',
                    Service.YANDEX: 'https://music.yandex.ru/album/17877728',
                    Service.YOUTUBE: 'https://www.youtube.com/playlist?list=OLAK5uy_l2KCVd6twQ-4KJAq5yUp1rut5w5KvpDp4',
                },
                thumbnail_url='https://i.scdn.co/image/ab67616d0000b27349fe16b18c5bc6b9dad782da',
            )
        ),

        (
            'https://music.yandex.ru/artist/701626',
            None,
        ),

        (
            'https://music.apple.com/ru/artist/architects/182821355?l=en',
            None,
        ),

        (
            'https://example.org/test',
            None,
        ),
    ]
)
def test_get_info(url: str, expected: Info | None):
    odesli = Odesli()
    actual = odesli.get_info(url)

    if expected is None:
        assert actual is None
        return

    assert actual.type == expected.type
    assert actual.artist_name == expected.artist_name
    assert actual.title == expected.title
    assert actual.thumbnail_url == expected.thumbnail_url

    assert len(actual.links) == len(expected.links)
    for key, val in actual.links.items():
        expected_val = expected.links[key]
        assert val.startswith(expected_val)
