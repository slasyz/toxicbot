import pytest

from toxic.features.music.services.odesli import Odesli


# TODO: use more services, for example https://songwhip.com/faq and direct APIs
from toxic.features.music.services.structs import Type, Service


@pytest.mark.parametrize(
    ['url', 'expected_none', 'expected_type', 'expected_artist_name', 'expected_title', 'expected_links', 'expected_thumbnail_url'],
    [
        (
            'https://open.spotify.com/track/0XauTwcR4Y44zdIS7yV2Jf?si=99dc49931ec14dcc',
            False,
            Type.SONG,
            ['Александр Смородинов, Он Юн', 'Он Юн, Александр Смородинов'],
            'Больше нет',
            {
                Service.APPLE_MUSIC: 'https://geo.music.apple.com/us/album/_/1454338948',
                Service.SPOTIFY: 'https://open.spotify.com/track/0XauTwcR4Y44zdIS7yV2Jf',
                Service.YANDEX: 'https://music.yandex.ru/track/50671259',
                Service.YOUTUBE: 'https://www.youtube.com/watch?v=fDEYWPvq_GQ',
            },
            'https://m.media-amazon.com/images/I/61h-+dzapJL.jpg',
        ),

        (
            'https://music.yandex.ru/album/3491806',
            False,
            Type.ALBUM,
            'Architects',
            'All Our Gods Have Abandoned Us',
            {
                Service.YANDEX: 'https://music.yandex.ru/album/3491806',
                Service.YOUTUBE: 'https://www.youtube.com/playlist?list=OLAK5uy_lbCwtJN6NJu_UEQrz2S_XSdF2COD3mq0w'
            },
            'https://avatars.yandex.net/get-music-content/38044/b41875c8.a.3491806-2/600x600',
        ),

        (
            'https://open.spotify.com/album/7qEap2Ip3FeBPEPLr9YaJc?si=yyCIl_QOS3OkdWM4crEUaw&dl_branch=1',
            False,
            Type.ALBUM,
            'Aikko',
            'Тёмные делишки',
            {
                Service.APPLE_MUSIC: 'https://geo.music.apple.com/us/album/_/1582455767',
                Service.SPOTIFY: 'https://open.spotify.com/album/7qEap2Ip3FeBPEPLr9YaJc',
                Service.YANDEX: 'https://music.yandex.ru/album/17877728',
                Service.YOUTUBE: 'https://www.youtube.com/playlist?list=OLAK5uy_l2KCVd6twQ-4KJAq5yUp1rut5w5KvpDp4',
            },
            'https://i.scdn.co/image/ab67616d0000b27349fe16b18c5bc6b9dad782da',
        ),

        (
            'https://music.yandex.ru/artist/701626',
            True,
            None,
            None,
            None,
            None,
            None,
        ),

        (
            'https://music.apple.com/ru/artist/architects/182821355?l=en',
            True,
            None,
            None,
            None,
            None,
            None,
        ),

        (
            'https://example.org/test',
            True,
            None,
            None,
            None,
            None,
            None,
        ),
    ]
)
async def test_get_info(url: str,
                        expected_none: bool,
                        expected_type: Type | None,
                        expected_artist_name: str | None,
                        expected_title: str | None,
                        expected_links: dict[Service, str] | None,
                        expected_thumbnail_url: str | None):
    odesli = Odesli()
    actual = await odesli.get_info(url)

    if expected_none:
        assert actual is None
        return

    assert actual.type == expected_type
    if isinstance(expected_artist_name, list):
        assert actual.artist_name in expected_artist_name
    else:
        assert actual.artist_name == expected_artist_name
    assert actual.title == expected_title
    assert actual.thumbnail_url == expected_thumbnail_url

    assert len(actual.links) == len(expected_links)
    for key, val in actual.links.items():
        expected_val = expected_links[key]
        assert val.startswith(expected_val)
