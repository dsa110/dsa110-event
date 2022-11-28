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
@click.option('--production', is_flag=True)
@click.option('--getdoi', is_flag=True)
@click.option('--files', type=list, default=[])
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
    print(f'Created metadata from {triggerfile}')

    # TODO: add version to metadata
    doi = metadata['identifiers'][0]['identifier']
    caltechdata.edit_ctd(metadata, files=files, production=production)  # publishes by default

    metadata_json = f'metadata_{triggerfile}'
    print(f'data published with doi {doi}. Saving {metadata_json}')

    with open(metadata_json, 'w') as fp:
        json.dump(metadata, fp)


@cli.command()
@click.argument('metadata_json')
@click.option('--production', is_flag=True)
@click.option('--files', type=list, default=[])
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

    doi = metadata['identifiers'][0]['identifier']
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
    dd['doi'] = dd['identifiers'][0]['identifier']
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
    """ takes json file with key-value pairs for create_voevent function.
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
@click.option('--send', type=bool, is_flag=True)
@click.option('--production', type=bool, is_flag=True)
def tns_create(inname, send, production):
    """ Create 
    report_filename is JSON format file with TNS metadata.
    """

    dd = caltechdata.set_metadata(triggerfile=inname)
    ve = voevent.create_voevent(**dd)
    dd2 = voevent.set_tns_dict(ve)  # this could also take phot_dict and event_dict to customize values

    # tmp file to send
    fn = f'tns_report_{ve.Why.Name}.json'
    if os.path.exists(fn):
        print(f"Removing older version of {fn}")
        os.remove(fn)
    voevent.write_tns(dd2, fn)
    if send:
        result = tns_api_bulk_report.send_report(fn, production)
