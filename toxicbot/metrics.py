from prometheus_client import Gauge, Summary, Counter


class Metrics:
    def __init__(self):
        self.messages = Gauge(name='messages', documentation='Size of messages table.', unit='total', namespace='toxic')
        self.updates = Counter(name='updates', documentation='Updates handled.', namespace='toxic')

        self.update_time = Summary(name='update', documentation='Update handle time.', unit='seconds', namespace='toxic')

        self.chain_predict = Summary(name='chain_predict', documentation='Chain prediction time.', unit='seconds', namespace='toxic')
