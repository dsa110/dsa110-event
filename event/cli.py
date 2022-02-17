import json
import click
from event import tns_api_bulk_report, caltechdata, voevent, labels

@click.group('dsaevent')
def cli():
    pass


@cli.command()
@click.argument('triggerfile')
@click.option('--production', type=bool, default=False)
@click.option('--doi', type=str, default=None)
def ctd_send(triggerfile, production, doi):
    """ Create entry at Caltech Data for data set
    An entry will be identified by an Id (integer).
    Requires triggerfile (as on h23)
    """

    idv = caltechdata.send_ctd(triggerfile=triggerfile, production=production, doi=doi)
    print(f'Triggerfile {triggerfile} uploaded as idv {idv}.')


@cli.command()
@click.argument('idv')
@click.argument('filenames')
@click.option('--production', type=bool, default=False)
def ctd_upload(idv, filenames, production):
    """ Edit entry at Caltech Data for data set to upload data given by filenames.
    idv is an integer that defines the Caltech Data entry.
    """

    caltechdata.edit_ctd(idv, filenames=filenames, production=production)


@cli.command()
@click.argument('triggerfile')
@click.argument('pngfile')
@click.option('--notes')
def archive_update(triggerfile, pngfile, notes)
    """ Use triggerfile to create updated events.csv file for dsa110-archive.
    Each triggerfile should also have an associated figure in png format.
    Notes can be appended to identify the nature of the event. Suggestions:
    - test
    - pulsar
    - frb
    - repeat of <frb name>
    """

    dd = caltechdata.set_metadata(triggerfile=triggerfile)
    dd['notes'] = notes
    columns = ['internalname', 'mjds', 'dm', 'width', 'snr', 'ra', 'dec', 'radecerr', 'notes']

    # use github python client to update dsa110-archive
    # update events.csv
    # add images/<pngfile>
    # push to github


@cli.command()
@click.argument('inname')
@click.argument('outname')
@click.option('--production', type=bool, default=False)
def create_voevent(inname, outname, production):
    """ takes json file with key-value pairs for create_voevent function.
    Required fields: fluence, p_flux, ra, dec, radecerr, dm, dmerr, width, snr, internalname, mjd, importance
    """

    dd = caltechdata.set_metadata(triggerfile=inname)
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
