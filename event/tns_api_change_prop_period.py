#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Avgust 2021

Developed and tested on:

- Linux 20.04 LTS
- Windows 10
- Python 3.8 (Spyder 4)

@author: Nikola Knezevic ASTRO DATA
"""

import requests
import json
from collections import OrderedDict
from os import environ

#----------------------------------------------------------------------------------

TNS                 = "www.wis-tns.org"
#TNS                 = "sandbox.wis-tns.org"
url_tns_api         = "https://" + TNS + "/api/set"

try:
    TNS_BOT_ID=environ['TNSBOTID']
    TNS_BOT_NAME=environ['TNSBOTNAME']
    TNS_API_KEY=environ['TNSKEY']
except KeyError:
    TNS_BOT_ID=None
    TNS_BOT_NAME=None
    TNS_API_KEY=None
    print('TNS env not found. TNS APIs will not work.')


# list that represents json file for setting prop period
prop_per        = [("objname", "20240215a"), ("reporting_groupid", "132"), ("end_prop_period_date", "2024-05-15"),
                       ("at", "0"), ("classification", "0"), ("spectra", "0"), ("frb", "1")]

#----------------------------------------------------------------------------------

def set_bot_tns_marker():
    tns_marker = 'tns_marker{"tns_id": "' + str(TNS_BOT_ID) + '", "type": "bot", "name": "' + TNS_BOT_NAME + '"}'
    return tns_marker

def format_to_json(source):
    parsed = json.loads(source, object_pairs_hook = OrderedDict)
    result = json.dumps(parsed, indent = 4)
    return result

def set_prop_period(prop_per):
    prop_period_url = url_tns_api + "/prop-period"
    tns_marker = set_bot_tns_marker()
    headers = {'User-Agent': tns_marker}
    json_file = OrderedDict(prop_per)
    pro_period_data = {'api_key': TNS_API_KEY, 'data': json.dumps(json_file)}
    response = requests.post(prop_period_url, headers = headers, data = pro_period_data)
    return response

#----------------------------------------------------------------------------------

response = set_prop_period(prop_per)
print(format_to_json(response.text))

"""
# EXAMPLE
set_prop_per        = [("objname", "2021ran"), ("reporting_groupid", "2"), ("end_prop_period_date", "2022-05-13"), 
                       ("at", "1"), ("classification", "0"), ("spectra", "0"), ("frb", "0")]
response = set_prop_period()
json_data = format_to_json(response.text)
print (json_data)
"""

#----------------------------------------------------------------------------------


