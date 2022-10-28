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
@click.option('--production', type=bool, default=False)
@click.option('--getdoi', is_flag=True)
@click.option('--files', type=list, default=[])
def ctd_send(triggerfile, production, getdoi, files):
    """ Use trigger json file (as on h23) to create entry at Caltech Data.
    Can optionally provide list of files (full path) to upload with entry.
    """

    metadata = caltechdata.create_ctd(triggerfile=triggerfile, production=production, getdoi=getdoi)
    print(f'{triggerfile} uploaded at Caltech Data')
    caltechdata.edit_ctd(metadata=metadata, filenames=filenames, production=production, files=files)
    doi = metadata['identifiers'][0]['identifier']
    print(f'{triggerfile} data published with doi {doi}')


@cli.command()
@click.argument('triggerfile')
@click.argument('doi')
@click.option('--notes')
@click.option('--csvfile', default='events.csv')
def archive_update(triggerfile, doi, notes, csvfile):
    """ Use triggerfile to create updated events.csv file for dsa110-archive.
    Each triggerfile should also have an associated doi.
    Notes can be appended to identify the nature of the event. Suggestions:
    - test
    - pulsar
    - frb
    - <known name>
    """

    dd = caltechdata.set_metadata(triggerfile=triggerfile)
    dd['notes'] = notes
    dd['doi'] = doi
    columns = ['internalname', 'mjds', 'dm', 'width', 'snr', 'ra', 'dec', 'radecerr', 'notes', 'doi']
    colheader = ['Internal Name', 'MJD', 'DM', 'Width', 'SNR', 'RA', 'Dec', 'RADecErr', 'Notes', 'DOI']

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

    dd = caltechdata.set_metadata(triggerfile=inname, production=production)
    ve = voevent.create_voevent(production=production, **dd)
    voevent.write_voevent(ve, outname=outname)


@cli.command()
@click.argument('inname')
@click.argument('destination')
def send_voevent(inname, destination):
    """ Read VOEvent XML file and send it somewhere
    """

    pass


@cli.command()
@click.argument('report_filename')
@click.option('--production', type=bool, default=False)
def tns_send(report_filename, production):
    """ Send event to TNS to be named.
    report_filename is JSON format file with TNS metadata.
    """

    result = tns_api_bulk_report.send_report(report_filename, production)
