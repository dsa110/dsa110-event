from gcn_kafka import Producer
import json
import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='GCN Kafka producer for DSA-110 events')
    parser.add_argument('--env', type=str, default='test', choices=['test', 'prod'],
                        help='Environment to use (test or prod, default: test)')
    parser.add_argument('--topic', type=str, default='gcn.notices.dsa110.frb',
                        help='Kafka topic to publish to (default: gcn.notices.dsa110.frb)')
    parser.add_argument('--json-file', type=str,
                        help='Path to JSON file to send (if not provided, sends test message)')
    parser.add_argument('--message', type=str,
                        help='JSON string to send (overrides --json-file)')
    
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

    # Connect as a producer (client "dsa110producer")
    # Warning: don't share the client secret with others.
    producer = Producer(client_id=client_id,
                        client_secret=client_secret,
                        domain=domain)

    # Determine what to send
    if args.message:
        jsondict = json.loads(args.message)
    elif args.json_file:
        with open(args.json_file, 'r') as f:
            jsondict = json.load(f)
    else:
        jsondict = {"event": 'hi'}
    
    json_data = json.dumps(jsondict).encode("utf-8")
    
    print(f"Sending to topic: {args.topic}")
    print(f"Message: {jsondict}")
    
    producer.produce(
        args.topic,
        json_data,
    )

    producer.flush()
    print("Message sent successfully")


if __name__ == '__main__':
    main()
