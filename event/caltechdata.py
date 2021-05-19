from caltechdata_api import caltechdata_edit, caltechdata_write
import json
from os import environ
import datetime

token = environ['TINDTOK']

# template metadata
with open('example.json', 'r') as fp:
    metadata = json.load(fp)

# modify metadata
metadata['publicationYear'] = datetime.datetime.now().year

# write metadata
res = caltechdata_write(metadata, token)
Id = res.rstrip('. ').split('/')[-1]

# upload supporting data
caltechdata_edit(token, Id, metadata={}, files='logo.gif')
