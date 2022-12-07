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


def create_ctd(triggerfile, files=[], getidv=True, getdoi=False, production=False, schema='43', version=None):
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
    if version is not None:
        metadata['version'] = version

    # write metadata
    if getidv:
        # create, but do not publish
        idv = caltechdata_write(metadata, token, production=production, schema=schema, files=files, publish=False)
        metadata['Identifiers'].append({'identifier': idv, 'identifierType': 'Caltech Data ID'})
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


def edit_ctd(metadata, idv=None, files=[], production=False, version=None, publish=True):
    """ Edit an entry at Caltech Data.
    Can provide metadata with url field to get caltech data idv or provide idv and metadata explicitly.
    metadata should be that returned by create_ctd. idv should be in metadata as an identifier.
    files is list of strings with full path to file for upload.
    """

    if version is not None:
        metadata['version'] = version

    if idv is None:
        for Iddict in metadata['Identifiers']:
            if Iddict['identifierType'] == 'Caltech Data ID':
                idv = Iddict['identifier']
                print(f'Got idv {idv} from metadata')

    assert idv is not None
    
    # upload supporting data
    caltechdata_edit(ids=idv, token=token, metadata=metadata, files=files, production=production, publish=publish)


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
        metadata['radecerr'] = 3.4*3600  # very conservative
        metadata['raerr'] = 30  # only correct at dec=0 for real-time beam
        metadata['decerr'] = 3.4*3600  # only correct at dec=0 for real-time beam

    # modify basic metadata
    if 'internalname' in metadata:
        metadata['Identifiers'] = [{'identifier': metadata['internalname'], 'identifierType': 'DSA-110 ID'}]
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


def set_tns_dict(dd, phot_dict={}, event_dict={}):
    """ Use metadata to assign values to TNS dictionary.

    Optional dictionary input to overload some fields:
    - phot_dict is dictionary for "photometry" keys to set: "snr", "flux", "flux_error", "fluence", "burst_width"
    - event_dict is dictionary for other TNS keys (from frb_report set): "remarks", "repeater_of_objid"
    """

    # TODO: optional "end_prop_period"
    # TODO: flux/flux_error
    # TODO: galactic_max_dm, galactic_max_dm_model
    
    tns_dict['frb_report']['0']["internal_name"] = metadata['internalname']
    tns_dict['frb_report']['0']["reporter"] = "Casey J. Law"

    tns_dict['frb_report']['0']['ra']['value'] = metadata['ra']
    tns_dict['frb_report']['0']['dec']['value'] = metadata['dec']
    tns_dict['frb_report']['0']['ra']['error'] = metadata['raerr']
    tns_dict['frb_report']['0']['dec']['error'] = metadata['decerr']
    tns_dict['frb_report']['0']["discovery_datetime"] = time.Time(metadata['mjds'], format="mjd").iso
    tns_dict['frb_report']['0']["reporting_groupid"] = 132  # DSA-110
    tns_dict['frb_report']['0']["groupid"] = 132  # DSA-110
    tns_dict['frb_report']['0']["at_type"] = 5  # FRBs

    tns_dict['frb_report']['0']["dm"] = metadata['dm']
    try:
        tns_dict['frb_report']['0']["dmerr"] = metadata['dmerr']
    except KeyError:
        pass
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["snr"] = metadata['snr']
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["burst_width"] = metadata['width']
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["filter_value"] = 129
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["instrument_value"] = 239
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["flux"] = 0   # TODO: set this
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["flux_error"] = 0   # TODO: set this
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["limiting_flux"] = 0
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["obsdate"] = dtstring
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["flux_units"] = "Jy"
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["ref_freq"] = "1405"
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["inst_bandwidth"] = "187.5"
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["channels_no"] = 768
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["sampling_time"] = 0.262

    # set photometry values
    for key, value in phot_dict.items():
        if key in tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]:
            print(f'Overloading event key {key} with {value}')
            tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"][key] = value
            
    # overload other values
    for key, value in event_dict.items():
        if key in tns_dict['frb_report']['0']:
            print(f'Overloading event key {key} with {value}')
            tns_dict['frb_report']['0'][key] = value
            
    return tns_dict

