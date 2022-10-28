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
    token = environ['RDMTOK']
except KeyError:
    dcp = None
    token = None

_install_dir = path.abspath(path.dirname(__file__))


def create_ctd(triggerfile, files=[], getidv=True, getdoi=False, production=False, schema='43'):
    """ Create entry at Caltech Data, but do not publish.
    triggerfile is json format for metadata (as typical on h23).
    files is (optional) list of strings with full path to file for upload.
    getidv will create entry at caltech data and add it to metadata
    getdoi will create doi and add it to metadata returned
    Upload takes time, so can be left blank and loaded alter via "edit_ctd" function.
    Returns metadata with triggerfile info and (optionally) a new doi.
    """

    if token is None:
        print('RDMTOK not set')
    
    metadata = set_metadata(triggerfile=triggerfile, schema=schema)

    # write metadata
    if getidv:
        # create, but do not publish
        idv = caltechdata_write(metadata, token, production=production, schema=schema, files=files, publish=False)
        metadata['alternateIdentifiers'].append({'alternateIdentifier': idv, 'alternateIdentifierType': 'Caltech Data id'})
        url = f'https://data.caltech.edu/records/{idv}'
        print(f"Created unpublished Caltech Data entry at {url.replace('records', 'uploads')}")
        if getdoi:
            metadata = get_doi(metadata, url, production=production)
            print(f"Created DOI to point to published location at {url}")
        else:
            print("No DOI created")
    else:
        print("No Caltech Data entry or DOI created")

    return metadata


def edit_ctd(idv=None, metadata=None, files=[], production=False):
    """ Edit an entry at Caltech Data.
    Can provide metadata with url field to get caltech data idv or provide idv and metadata explicitly.
    metadata should be that returned by create_ctd. idv should be in metadata as an identifier.
    files is list of strings with full path to file for upload.
    """

    if idv is None:
        for altid in metadata['alternateIdentifiers']:
            if altid['alternateIdentifierType'] == 'Caltech Data id':
                idv = altid['alternateIdentifier']
                print(f'Got idv {idv} from metadata')

    assert idv is not None
    
    # upload supporting data
    caltechdata_edit(ids=idv, token=token, metadata=metadata, files=files, production=production, publish=True)


def set_metadata(triggerfile=None, schema='43', notes=None):
    """ Create dict with metadata for caltechdata/datacite.
    triggerfile overloads fields in template fields (format as found on h23).
    schema can be '43' or '42' and defines template json file.
    """

    # template metadata
    with open(f'{_install_dir}/data/example{schema}.json', 'r') as fp:
        metadata = json.load(fp)

    required = ['internalname', 'mjds', 'dm', 'width', 'snr', 'ra', 'dec', 'radecerr']
    preferred = ['fluence', 'p_flux', 'importance', 'dmerr']

    # set values
    if triggerfile is not None:   # typical format as found on h23
        trigger = labels.readfile(filename=triggerfile)
        for k, v in trigger.items():
            if k in required + preferred:
                metadata[k] = v
        metadata['internalname'] = trigger['trigname']
        metadata['width'] = 0.262144*trigger['ibox']   # TODO: use cnf?
        if 'radecerr' not in metadata:
            metadata['radecerr'] = 2

    # modify basic metadata
    if 'internalname' in metadata:
        metadata['alternateIdentifiers'] = [{'alternateIdentifier': metadata['internalname'], 'alternateIdentifierType': 'DSA-100 internal id'}]
    dt = datetime.datetime.now()
    metadata['publicationYear'] = f'{dt.year:04}'
    metadata['dates'] = [{'date': f'{dt.year:04}-{dt.month:02}-{dt.day:02}', 'dateType': 'Created'}]  # dateType can also be "Updated"
    metadata['titles'] = [{'title': f'DSA-110 Data for Candidate Fast Radio Burst {metadata["internalname"]}'}]

    if notes is not None:
        description = {"description": notes, "descriptionType": "TechnicalInfo"}
        metadata['descriptions'].append(description)

    return metadata


def get_doi(metadata, url, production=False):
    """ Use datacite to get DOI for metadata.
    DOI redirects to url.
    """

    # development
    dcprefix_dev = '10.22013'
#    dcurl_dev = 'http://doi.test.datacite.org'
    # production
    dcprefix_prod = '10.25800'
#    dcurl_prod = 'http://doi.datacite.org'

    if production:
        prefix = dcprefix_prod
    else:
        prefix = dcprefix_dev

    # generate doi
    if dcp is None:
        print("DATACITEPWD not set")
    d = DataCiteRESTClient(username='CALTECH.OVRO', password=dcp, prefix=prefix, test_mode=(not production))
    doi = d.public_doi(metadata, url)
    metadata['identifiers'] = [{'identifier': doi, 'identifierType': 'DOI'}]

    return metadata
