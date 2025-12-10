from gcn_kafka import Producer
import json
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

# Connect as a consumer (client "dsa110producer")
# Warning: don't share the client secret with others.
producer = Producer(client_id=client_id,
                    client_secret=client_secret,
                    domain=domain)

#jsondict = json.load(jsonfile)
jsondict = {"event": 'hi'}
TOPIC = 'gcn.notices.dsa110.frb'

json_data = json.dumps(jsondict).encode("utf-8")

producer.produce(
	TOPIC,
	json_data,
)

producer.flush()
