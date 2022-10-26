import json
from os import environ, path
import datetime
from event import labels

try:
    from datacite import DataCiteRESTClient
except ImportError:
    pass

try:
    from caltechdata_api import caltechdata_edit, caltechdata_write
except ImportError:
    pass

try:
    dcp = environ['DATACITEPWD']
    token = environ['TINDTOK']
except KeyError:
    dcp = None
    token = None

_install_dir = path.abspath(path.dirname(__file__))


def send_ctd(triggerfile, doi=None, filenames=[], production=False, schema='43'):
    """ Create entry at Caltech Data.
    triggerfile is json format for metadata (as typical on h23).
    filenames is (optional) list of strings with full path to file for upload.
    Upload takes time, so can be left blank and loaded alter via "edit_ctd" function.
    """
    if token is None:
        print('TINDTOK not set')
    
    metadata = set_metadata(triggerfile=triggerfile, doi=doi, schema=schema, production=production)

    # write metadata
    res = caltechdata_write(metadata, token, production=production, schema=schema, filenames=filenames)
    idv = res.rstrip('. ').split('/')[-1]

    return idv


def edit_ctd(idv, metadata={}, filenames=[], production=False):
    """ Edit an entry at Caltech Data.
    metadata can be emtpy dict ({}) and filenames a list of files associate with existing idv.
    filenames is list of strings with full path to file for upload.
    """
    
    # upload supporting data
    caltechdata_edit(ids=idv, token=token, metadata=metadata, files=filenames, production=production)


def set_metadata(triggerfile=None, doi=None, schema='43', notes=None, production=False):
    """ Create dict with metadata for caltechdata/datacite.
    triggerfile overloads fields in template fields (format as found on h23).
    doi can be provided, but if not, one will be generated.
    schema can be '43' or '42' and defines template json file.
    """

    # template metadata
    with open(path.join(_install_dir, f'data/example{schema}.json'), 'r') as fp:
        metadata = json.load(fp)

    required = ['internalname', 'mjds', 'dm', 'width', 'snr', 'ra', 'dec', 'radecerr']
    preferred = ['fluence', 'p_flux', 'importance', 'dmerr']

    # set values
    if triggerfile is not None:   # typical format as found on h23
        trigger = labels.readfile(triggerfile)
        for k, v in trigger.items():
            if k in required + preferred:
                metadata[k] = v
        metadata['internalname'] = trigger['trigname']
        metadata['width'] = 0.262144*trigger['ibox']   # TODO: use cnf?
        metadata['radecerr'] = 1   # TODO: set to synthesized beam size

    # modify basic metadata
    if 'internalname' in metadata:
        metadata['alternateIdentifiers'] = [{'alternateIdentifier': metadata['internalname'],}]
#                                             'alternateIdentifierType': '?'}]
    dt = datetime.datetime.now()
    metadata['publicationYear'] = f'{dt.year:04}'
    metadata['dates'] = [{'date': f'{dt.year:04}-{dt.month:02}-{dt.day:02}', 'dateType': 'Created'}]  # dateType can also be "Updated"
    metadata['titles'] = [{'title': f'DSA-110 Data for Candidate Fast Radio Burst {metadata["internalname"]}'}]

    # can provide doi or have one generated by datacite
    doi = get_doi(metadata, doi=doi, production=production)
            
    metadata['identifiers'] = [{'identifier': doi, 'identifierType': 'DOI'}]
    if notes is not None:
        description = {"description": notes, "descriptionType": "TechnicalInfo"}
        metadata['descriptions'].append(description)

    return metadata


def get_doi(metadata, doi=None, production=False):
    """ Use datacite to get DOI for metadata
    """

    # development
    dcprefix_dev = '10.22013'
    dcurl_dev = 'http://doi.test.datacite.org'
    # production
    dcprefix_prod = '10.25800'
    dcurl_prod = 'http://doi.datacite.org'

    if production:
        url = dcurl_prod
        prefix = dcprefix_prod
    else:
        url = dcurl_dev
        prefix = dcprefix_dev

    # either generate doi or fix doi without prefix
    if doi is not None:
        if prefix not in doi:
            print(f'DOI provided ({doi}) does not have required prefix ({prefix}). Adding prefix.')
            doi = prefix + '/' + doi
    else:
        if dcp is None:
            print("DATACITEPWD not set")
        d = DataCiteRESTClient(username='CALTECH.OVRO', password=dcp, prefix=prefix, test_mode=(not production))
        doi = d.public_doi(metadata, url)

    return doi
