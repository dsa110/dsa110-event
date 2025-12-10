from gcn_kafka import Consumer
import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='GCN Kafka consumer for DSA-110 events')
    parser.add_argument('--env', type=str, default='test', choices=['test', 'prod'],
                        help='Environment to use (test or prod, default: test)')
    parser.add_argument('--topic', type=str, default='gcn.notices.dsa110.frb',
                        help='Kafka topic to subscribe to (default: gcn.notices.dsa110.frb)')
    parser.add_argument('--timeout', type=int, default=1,
                        help='Consumer timeout in seconds (default: 1)')
    
    args = parser.parse_args()
    
    if args.env == 'test':
        print("using test credentials")
        domain = 'test.gcn.nasa.gov'
        client_id = os.environ.get('GCN_ID_PRO_TEST', '')
        client_secret = os.environ.get('GCN_SECRET_PRO_TEST', '')
    elif args.env == 'prod':
        print("using prod credentials")
        domain = 'gcn.nasa.gov'
        client_id = os.environ.get('GCN_ID_PRO', '')
        client_secret = os.environ.get('GCN_SECRET_PRO', '')
    else:
        print(f"env ({args.env}) not recognized")
        sys.exit(1)

    # Connect as a consumer (client "dsa110consumer")
    # Warning: don't share the client secret with others.
    consumer = Consumer(client_id=client_id,
                        client_secret=client_secret,
                        domain=domain,
                        config={'auto.offset.reset': 'earliest'})

    # Subscribe to topics and receive alerts
    consumer.subscribe([args.topic])
    print(f"Subscribed to topic: {args.topic}")
    
    while True:
        for message in consumer.consume(timeout=args.timeout):
            if message.error():
                print(message.error())
                continue
            # Print the topic and message ID
            print(f'topic={message.topic()}, offset={message.offset()}')
            value = message.value()
            print(value)


if __name__ == '__main__':
    main()
