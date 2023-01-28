from dataclasses import dataclass

from toxic.modules.music.services.structs import Service, Info, Type

SERVICES_ORDER = [
    Service.APPLE_MUSIC,
    Service.SPOTIFY,
    Service.YANDEX,
    Service.YOUTUBE,
    Service.BOOM,
]


@dataclass
class StreamingLink:
    # TODO: do something with StreamingLink and tuple[Service, str]
    name: str
    link: str


@dataclass
class Content:
    text: str
    buttons: list[StreamingLink]


def get_content(info: Info) -> Content:
    text = f'Исполнитель: <b>{info.artist_name}</b>'
    if info.type is not None and info.type != Type.ARTIST:
        text += f'\n{info.type.value}: <b>{info.title}</b>'

    services = []
    for service in SERVICES_ORDER:
        link = info.links.get(service)
        if link is not None:
            services.append(StreamingLink(service.value, link))

    return Content(text, services)
