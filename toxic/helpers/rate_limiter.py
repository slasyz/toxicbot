import logging
from dataclasses import dataclass
from datetime import datetime

from toxic.messenger.messenger import Messenger


@dataclass
class Bucket:
    last_check: datetime
    allowance: float


class RateLimiter:
    def __init__(self, rate: int, per: int, reply: str, messenger: Messenger):
        self.rate = rate
        self.per = per
        self.reply = reply
        self.messenger = messenger

        self.buckets: dict[(int, int), Bucket] = {}

    def handle(self, message) -> bool:
        if self.discard(message.chat_id, message.from_user.id):
            self.messenger.reply(message, self.reply)
            return True

        return False

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
            logging.info('Discarding command from (%d, %d), bucket: %s', chat, user, bucket)
            return True

        bucket.allowance -= 1
        return False
