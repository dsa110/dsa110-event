import click
from event import tns_api_bulk_report, caltechdata, voevent

@click.group('dsaevent')
def cli():
    pass

@cli.command()
@click.argument('inname')
@click.argument('outname')
def create_voevent(inname, outname):
    ve = voevent.create_voevent(inname)
    voevent.create_voevent(ve, outname=outname)


@cli.command()
@click.argument('report_filename')
@click.option('--production', type=bool, default=False)
def tns_send(report_filename, production):
    tns_api_bulk_report.send_report(report_filename, production)


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
