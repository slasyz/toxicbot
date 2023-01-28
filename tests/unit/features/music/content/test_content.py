import pytest

from toxic.modules.music.generator.content import Content, StreamingLink, get_content
from toxic.modules.music.services.structs import Info, Service, Type


@pytest.mark.parametrize(
    ['info', 'expected'],
    [
        (
            Info(
                type=Type.SONG,
                artist_name='Well-Known Artist',
                title='His/Her Hit [Bass Boosted]',
                links={
                    Service.BOOM: 'https://example.org/boom_link',
                    Service.YOUTUBE: 'https://example.org/youtube_link',
                },
                thumbnail_url='https://example.org/pic.png',
            ),
            Content(
                text='''Исполнитель: <b>Well-Known Artist</b>
Трек: <b>His/Her Hit [Bass Boosted]</b>''',
                buttons=[
                    StreamingLink(name='YouTube', link='https://example.org/youtube_link'),
                    StreamingLink(name='Boom', link='https://example.org/boom_link'),
                ]
            )
        ),

        (
            Info(
                type=Type.ALBUM,
                artist_name='Алла Пугачёва',
                title='Золотые хиты',
                links={
                    Service.BOOM: 'https://example.org/boom_link',
                    Service.YOUTUBE: 'https://example.org/youtube_link',
                },
                thumbnail_url='https://example.org/pic.png',
            ),
            Content(
                text='''Исполнитель: <b>Алла Пугачёва</b>
Альбом: <b>Золотые хиты</b>''',
                buttons=[
                    StreamingLink(name='YouTube', link='https://example.org/youtube_link'),
                    StreamingLink(name='Boom', link='https://example.org/boom_link'),
                ]
            )
        ),

        (
            Info(
                type=Type.ARTIST,
                artist_name='Architects',
                title='#!@#!@#',
                links={
                    Service.YOUTUBE: 'https://example.org/youtube_link',
                    Service.SPOTIFY: 'https://example.org/spotify_link',
                    Service.APPLE_MUSIC: 'https://example.org/apple_music_link',
                },
                thumbnail_url='https://example.org/pic.png',
            ),
            Content(
                text='Исполнитель: <b>Architects</b>',
                buttons=[
                    StreamingLink(name='Apple Music', link='https://example.org/apple_music_link'),
                    StreamingLink(name='Spotify', link='https://example.org/spotify_link'),
                    StreamingLink(name='YouTube', link='https://example.org/youtube_link'),
                ]
            )
        ),
    ]
)
def test_get_content(info: Info, expected: Content):
    actual = get_content(info)
    assert actual == expected
