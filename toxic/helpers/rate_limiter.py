from dataclasses import dataclass
from datetime import datetime

import aiogram
from loguru import logger


@dataclass
class Bucket:
    last_check: datetime
    allowance: float


class RateLimiter:
    def __init__(self, rate: int, per: int, reply: str):
        self.rate = rate
        self.per = per
        self.reply = reply

        self.buckets: dict[tuple[int, int], Bucket] = {}

    def handle(self, message: aiogram.types.Message) -> str | None:
        if message.from_user is None:
            return None
        if self.discard(message.chat.id, message.from_user.id):
            return self.reply

        return None

    def discard(self, chat: int, user: int) -> bool:
        now = datetime.now()

        bucket = self.buckets.get((chat, user))
        if bucket is None:
            bucket = Bucket(
                last_check=now,
                allowance=self.rate,
            )
            self.buckets[(chat, user)] = bucket

        time_passed = (now - bucket.last_check).total_seconds()
        bucket.last_check = now
        bucket.allowance += time_passed * (self.rate / self.per)

        if bucket.allowance > self.rate:
            bucket.allowance = self.rate

        if bucket.allowance < 1:
            logger.info('Discarding command from ({}, {}), bucket: {}.', chat, user, bucket)
            return True

        bucket.allowance -= 1
        return False
