class Delayer:
    def __init__(self, total: int, keepalive: int):
        self.total = total
        self.keepalive = keepalive

    def __iter__(self):
        for _ in range(int(self.total // self.keepalive)):
            yield self.keepalive

        left = self.total % self.keepalive
        if left > 0:
            yield left


class DelayerFactory:
    @staticmethod
    def create(total: int, keepalive: int) -> Delayer:
        return Delayer(total, keepalive)
