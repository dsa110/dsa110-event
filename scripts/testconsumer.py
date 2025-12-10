from gcn_kafka import Consumer
import os

env = 'test'

if env == 'test':
    print("using test credentials")
    domain = 'test.gcn.nasa.gov'
    client_id = os.environ.get('GCN_ID_PRO_TEST', '')
    client_secret = os.environ.get('GCN_SECRET_PRO_TEST', '')
elif env == 'prod':
    print("using prod credentials")
    domain = 'gcn.nasa.gov'
    client_id = os.environ.get('GCN_ID_PRO', '')
    client_secret = os.environ.get('GCN_SECRET_PRO', '')
else:
    print(f"env ({env}) not recognized")
    sys.exit(1)

# Connect as a consumer (client "dsa110consumer")
# Warning: don't share the client secret with others.
consumer = Consumer(client_id=client_id,
                    client_secret=client_secret,
                    domain=domain,
                    config = {'auto.offset.reset': 'earliest'})

# Subscribe to topics and receive alerts
consumer.subscribe(['gcn.notices.dsa110.frb'])
while True:
    for message in consumer.consume(timeout=1):
        if message.error():
            print(message.error())
            continue
        # Print the topic and message ID
        print(f'topic={message.topic()}, offset={message.offset()}')
        value = message.value()
        print(value)
