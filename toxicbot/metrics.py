from prometheus_client import Gauge, Summary, Counter

messages = Gauge(name='messages', documentation='Size of messages table.', unit='total', namespace='toxic')
updates = Counter(name='updates', documentation='Updates handled.', namespace='toxic')

update_time = Summary(name='update', documentation='Update handle time.', unit='seconds', namespace='toxic')

chain_predict = Summary(name='chain_predict', documentation='Chain prediction time.', unit='seconds', namespace='toxic')
