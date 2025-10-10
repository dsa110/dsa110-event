import json
import os
from gcn_kafka import Producer
from astropy.time import Time

def gcn_send(jsonfile, env='test', topic='gcn.notices.dsa110.frb'):
    """ Use trigger json to send GCN notice
    """

    if env == 'test':
        domain = 'test.gcn.nasa.gov'
        client_id = os.environ.get('GCN_ID_PRO_TEST', '')
        client_secret = os.environ.get('GCN_SECRET_PRO_TEST', '')
    else:
        domain = 'gcn.nasa.gov'
        print("Still need to get credentials for production mode")
        sys.exit(1)

    # Connect as a producer (client "dsa110")
    producer = Producer(client_id=client_id, client_secret=client_secret, domain=domain)

    # Initialize and overload dict with json values
    jsondata = {'$schema': 'https://gcn.nasa.gov/schema/v6.0.0/gcn/notices/mission/SchemaName.schema.json'}
    with open(jsonfile, 'r') as fp:
        trig = json.load(fp)

    jsondata["alert_type"] = "initial"
    jsondata["trigger_time"] = Time(trig["mjds"], format="mjd").isot
    jsondata["id"] = trig["trigname"]
    jsondata["snr"] = trig["snr"]
    jsondata["dm"] = trig["dm"]
    jsondata["event_duration"] = 0.262144*trig["ibox"] # ms TODO: check
    jsondata["ra"] = trig["ra"]
    jsondata["dec"] = trig["dec"]
    jsondata["ra_dec_error"] = [0.016, 0.016]  # 1' is about the zenith search beam width
    jsondata["importance"] = trig["probability"]
        
    # JSON data converted to byte string format
    data = json.dumps(jsondata).encode("utf-8")

    producer.produce(topic, data)
    producer.flush()
