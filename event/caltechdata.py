from caltechdata_api import caltechdata_edit, caltechdata_write
import json
from os import environ, path
import datetime

token = environ['TINDTOK']
_install_dir = path.abspath(path.dirname(__file__))

# template metadata
with open(path.join(_install_dir, 'data/example.json'), 'r') as fp:
    metadata = json.load(fp)


def send_ctd(dictin={}, filenames=[], production=False):
    """ Create entry at Caltech Data.
    dictin overloads fields in template dictionary.
    filenames is list of strings with full path to file for upload.
    Upload takes time, so can be left blank and loaded alter via "edit_ctd" function.
    """

    # modify basic metadata
    metadata['alternateIdentifiers'] = [{'alternateIdentifier': internalname,
                                         'alternateIdentifierType': '?'}]
    metadata['publicationYear'] = datetime.datetime.now().year
    metadata['dates'] = [{'date': 'yyyy-mm-dd', 'dateType': 'Created'}]  # dateType can also be "Updated"
#    metadata['descriptions'][{'description': description, 'descriptionType': 'Abstract']}
#    metadata['formats'] = ['FITS', 'filterbank', 'png']  # or just one zip?
    
    # overload metadata
    for key, value in dictin.items():
        if key in metadata:
            print(f'Overloading metadata key {key} with {value}')
            metadata[key] = value

    # write metadata
    res = caltechdata_write(metadata, token, filenames, production=production)
    Id = res.rstrip('. ').split('/')[-1]

    return Id

def edit_ctd(Id, metadata={}, filenames=[], production=False):
    """ Edit an entry at Caltech Data.
    metadata can be emtpy dict ({}) and filenames a list of files associate with existing Id.
    filenames is list of strings with full path to file for upload.
    """
    
    # upload supporting data
    caltechdata_edit(token, Id, metadata=metadata, filenames=filenames, production=production)
