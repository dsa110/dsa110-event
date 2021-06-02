import json
from os import environ, path
import datetime
from datacite import DataCiteRESTClient
from caltechdata_api import caltechdata_edit, caltechdata_write

dcprefix = '10.22013'   # prefix for test.datacite.org
dcurl = 'doi.test.datacite.org'
dcp = environ['DATACITEPWD']
token = environ['TINDTOK']
_install_dir = path.abspath(path.dirname(__file__))

# template metadata
with open(path.join(_install_dir, 'data/example43.json'), 'r') as fp:
    metadata = json.load(fp)


def send_ctd(dictin={}, filenames=[], production=False):
    """ Create entry at Caltech Data.
    dictin overloads fields in template dictionary.
    filenames is list of strings with full path to file for upload.
    Upload takes time, so can be left blank and loaded alter via "edit_ctd" function.
    """

    metadata = get_metadata(dictin)

    # write metadata
    res = caltechdata_write(metadata, token, filenames, production=production)  # schema="43" if using new affiliation
    Id = res.rstrip('. ').split('/')[-1]

    return Id

def get_metadata(dictin):
    """ 
    """

    # modify basic metadata
    metadata['alternateIdentifiers'] = [{'alternateIdentifier': internalname,
                                         'alternateIdentifierType': '?'}]
    metadata['publicationYear'] = datetime.datetime.now().year
    metadata['dates'] = [{'date': 'yyyy-mm-dd', 'dateType': 'Created'}]  # dateType can also be "Updated"
    #    metadata['formats'] = ['FITS', 'filterbank', 'png']  # or just one zip?

    # overload metadata
    for key, value in dictin.items():
        if key in metadata:
            print(f'Overloading metadata key {key} with {value}')
            metadata[key] = value

    # can provide doi or have one generated by datacite
    doi = get_doi(metadata)  # TODO: check whether it is returned or just added to metadata dict
    metadata['identifiers'] = [{'identifier': doi, 'identifierType': 'DOI'}]  

    return metadata


def get_doi(metadata, url=dcurl):
    """ Use datacite to get DOI for metadata
    """

    d = DataCiteRESTClient(username='CALTECH.OVRO', password=dcp, prefix=dcprefix, test_mode=True)
    d.public_doi(metadata, url)


def edit_ctd(Id, metadata={}, filenames=[], production=False):
    """ Edit an entry at Caltech Data.
    metadata can be emtpy dict ({}) and filenames a list of files associate with existing Id.
    filenames is list of strings with full path to file for upload.
    """
    
    # upload supporting data
    caltechdata_edit(token, Id, metadata=metadata, filenames=filenames, production=production)
