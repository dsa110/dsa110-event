import os
import json
import click
import csv
from event import tns_api_bulk_report, caltechdata, voevent, labels

@click.group('dsaevent')
def cli():
    pass


@cli.command()
@click.argument('triggerfile')
@click.option('--production', is_flag=True, default=False, show_default=True)
@click.option('--getdoi', is_flag=True, default=False, show_default=True)
@click.option('--files', type=str, default=None)
@click.option('--version', type=str, default=0.1)
def ctd_send(triggerfile, production, getdoi, files, version):
    """ Use trigger json file (as on h23) to create entry at Caltech Data.
    Can optionally provide list of files (full path) to upload with entry.
    versions:
    - use version 0.x to refer to nonstandard, ad hoc release (e.g., not a complete package)
    - use version 1.0 to refer to standard data package with "final" processing (e.g., in January)
    - use version 1.x to refer to minor updates that don't affect science
    - use version x.0 to refer to major fixes with (for x>1)
    """

    metadata = caltechdata.create_ctd(triggerfile=triggerfile, production=production, getdoi=getdoi, version=version)
    for Iddict in metadata['identifiers']:
        if Iddict['identifierType'] == 'DOI':
            doi = Iddict['identifier']
            print(f'Got doi {doi} from metadata')

    print(f'Created metadata from {triggerfile} with doi {doi}')

    metadata_json = f'metadata_{triggerfile}'
    print(f'Saving {metadata_json}')
    with open(metadata_json, 'w') as fp:
        json.dump(metadata, fp)

    caltechdata.edit_ctd(metadata, files=files, production=production)  # publishes by default



@cli.command()
@click.argument('metadata_json')
@click.option('--production', is_flag=True, default=False, show_default=True)
@click.option('--files', type=str, default=None)
@click.option('--description', type=str, default=None)
@click.option('--version', type=str, default=None)
def ctd_update(metadata_json, production, files, description, version):
    """ Use metadata json file (from ctd_create) to update entry at Caltech Data.
    Can update description, files, version.
    versions:
    - use version 0.x to refer to nonstandard, ad hoc release (e.g., not a complete package)
    - use version 1.0 to refer to standard data package with "final" processing (e.g., in January)
    - use version 1.x to refer to minor updates that don't affect science
    - use version x.0 to refer to major fixes with (for x>1)
    """

    with open(metadata_json, 'r') as fp:
        metadata = json.load(fp)
    print(f'Read metadata from {metadata_json}')

    if description is not None:
        metadata['descriptions'][0]['description'] = description
    if version is not None:
        metadata['version'] = version

    # TODO: add version to metadata
    caltechdata.edit_ctd(metadata, production=production, files=files, publish=True)

    for Iddict in metadata['identifiers']:
        if Iddict['identifierType'] == 'DOI':
            doi = Iddict['identifier']
            print(f'Got doi {doi} from metadata')
    print(f'edited published entry with doi {doi}. Saving {metadata_json}')

    with open(metadata_json, 'w') as fp:
        json.dump(metadata, fp)


@cli.command()
@click.argument('metadata_json')
@click.option('--notes')
@click.option('--csvfile', default='events.csv')
def archive_update(metadata_json, notes, csvfile):
    """ Use metadata_json saved by ctd_send to add line to  events.csv file for dsa110-archive.
    metadata file should have doi and version.
    Notes can be appended to identify the nature of the event. Suggestions:
    - test
    - pulsar
    - frb
    - <known name>
    """

    with open(metadata_json, 'r') as fp:
        dd = json.load(fp)

    dd['notes'] = notes

    for Iddict in dd['identifiers']:
        if Iddict['identifierType'] == 'DOI':
            doi = Iddict['identifier']
            dd['doi'] = doi
            print(f'Got doi {doi} from metadata')
    
    columns = ['internalname', 'mjds', 'dm', 'width', 'snr', 'ra', 'dec', 'radecerr', 'notes', 'version', 'doi']
    colheader = ['Internal Name', 'MJD', 'DM', 'Width', 'SNR', 'RA', 'Dec', 'RADecErr', 'Notes', 'Version', 'doi']

    # verify that columns are correct?

    row = [dd[column] for column in columns]
    if os.path.exists(csvfile):
        code = 'a'
    else:
        code = 'w'
    with open(csvfile, code) as fp:
        csvwriter = csv.writer(fp)
        if code == 'w':
            csvwriter.writerow(colheader)  # no need if appending
        csvwriter.writerow(row)

    # then use github python client to update dsa110-archive
    # and push to github


@cli.command()
@click.argument('inname')
@click.argument('outname')
@click.option('--production', type=bool, default=False)
def create_voevent(inname, outname, production):
    """ Takes T2 json (triggerfile) with key-value pairs for create_voevent function.
    Required fields: fluence, p_flux, ra, dec, radecerr, dm, dmerr, width, snr, internalname, mjd, importance
    """

    dd = caltechdata.set_metadata(triggerfile=inname)
    ve = voevent.create_voevent(**dd)
    voevent.write_voevent(ve, outname=outname)


@cli.command()
@click.argument('inname')
@click.argument('destination')
def send_voevent(inname, destination):
    """ Read VOEvent XML file and send it somewhere
    """

    pass


@cli.command()
@click.argument('inname')
@click.option('--send', type=bool, default=False, is_flag=True, show_default=True)
@click.option('--production', type=bool, default=False, is_flag=True, show_default=True)
@click.option('--repeater_of_objid', type=str, default=None)
@click.option('--remarks', type=str, default=None)
def tns_create(inname, send, production, repeater_of_objid, remarks):
    """ Takes T2 triggerfile to create report_filename in JSON format file with TNS metadata.
    Arguments send and production are boolean flags to do something with tns json file.
    Common optional fields are repeater_of_objid and remarks.
    """

    event_dict, phot_dict = {}, {}
    if repeater_of_objid is not None:
        event_dict['repeater_of_objid'] = repeater_of_objid
    if remarks is not None:
        event_dict['remarks'] = remarks

    dd = caltechdata.set_metadata(triggerfile=inname)
# TODO: test doing direct to TNS json instead of using voevent
#    dd2 = caltechdata.set_tns_dict(dd, phot_dict=phot_dict, event_dict=event_dict)
    ve = voevent.create_voevent(**dd)
    dd2 = voevent.set_tns_dict(ve, phot_dict=phot_dict, event_dict=event_dict)

    # tmp file to send
    fn = f'tns_report_{ve.Why.Name}.json'
    if os.path.exists(fn):
        print(f"Removing older version of {fn}")
        os.remove(fn)
    voevent.write_tns(dd2, fn)
    if send:
        result = tns_api_bulk_report.send_report(fn, production)


@cli.command()
@click.argument('inname')
@click.option('--production', type=bool, default=False, is_flag=True, show_default=True)
@click.option('--send', type=bool, default=False, is_flag=True, show_default=True)
def tns_send(inname, production, send):
    """ Take TNS json file (created by tns_create) and send it to TNS.
    production is a boolean flags.
    """

    # tmp file to send
    if not os.path.exists(inname):
        print(f"file {inname} not found")

    if send:
        result = tns_api_bulk_report.send_report(inname, production)
