import click
from event import tns_api_bulk_report, caltechdata, voevent

@click.group('dsaevent')
def cli():
    pass

@cli.command()
@click.argument('inname')
@click.argument('outname')
@click.option('--production', type=bool, default=False)
def create_voevent(inname, outname, production):
    """ takes json file with key-value pairs for create_voevent function.
    Required fields: fluence, p_flux, ra, dec, radecerr, dm, dmerr, width, snr, internalname, mjd, importance
    """

    with open(inname, 'r') as fp:
        indict = json.load(fp)
    ve = voevent.create_voevent(production=production, **indict)
    voevent.create_voevent(ve, outname=outname)


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


@cli.command()
@click.argument('report_filename')
@click.option('--production', type=bool, default=False)
def ctd_send(report_filename, production):
    with open(report_filename, 'r') as fp:
        dd = json.load(fp)

    dictin = dd  # TODO: extract relevant fields from TNS json for ctd

    caltechdata.send_ctd(dictin, production=production)

    
@cli.command()
@click.argument('Id')
@click.argument('filenames')
@click.option('--production', type=bool, default=False)
def ctd_upload(Id, filenames, production):
    caltechdata.edit_ctd(Id, filenames=filenames, production=production)
