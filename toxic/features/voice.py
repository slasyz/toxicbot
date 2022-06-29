from io import BytesIO
from typing import IO

import aiohttp

from toxic.helpers import consts
from toxic.helpers.retry import with_retry_async

MAX_ATTEMPTS = 3
MAX_ERROR_LENGTH = 100

GENERATE_ENDPOINT = 'https://nextup.com/ivona/php/nextup-polly/CreateSpeech/CreateSpeechGet3.php'


class InvalidLinkException(Exception):
    pass


class VoiceService:
    async def load(self, text: str) -> IO:
        raise NotImplementedError()


class NextUpService(VoiceService):
    async def load(self, text: str) -> IO:
        # TODO: proxy
        link = await self.generate_link(text)

        async with aiohttp.ClientSession() as session, session.get(link) as audio:
            f = BytesIO(await audio.read())
            return f

    @with_retry_async(MAX_ATTEMPTS, (InvalidLinkException,))
    async def generate_link(self, text):
        # TODO: proxy
        async with aiohttp.ClientSession() as session:
            req = await session.get(
                url=GENERATE_ENDPOINT,
                params={
                    'voice': 'Maxim',
                    'language': 'ru-RU',
                    'text': text
                },
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    'Referer': 'https://nextup.com/ivona/russian.html',
                }
            )
            with req:
                if not consts.LINK_REGEXP.match(req.text):
                    result = req.text[:min(len(await req.text()), MAX_ERROR_LENGTH)]
                    raise InvalidLinkException(result)

                return req.text
