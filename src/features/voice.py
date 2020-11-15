from io import BytesIO
from typing import IO

import requests

GENERATE_ENDPOINT = 'https://nextup.com/ivona/php/nextup-polly/CreateSpeech/CreateSpeechGet3.php'


class VoiceService:
    def load(self, text: str) -> IO:
        raise NotImplementedError()


class NextUpService(VoiceService):
    def load(self, text: str) -> IO:
        # TODO: proxy
        link = self._generate_link(text)

        with requests.get(link) as audio:
            f = BytesIO(audio.content)
            return f

    def _generate_link(self, text):
        # TODO: proxy
        req = requests.get(
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
            return req.text
