import click
import tns_api_bulk_report
import caltechdata

@click.group('dsaevent')
def cli():
    pass

@cli.command()
@cli.argument(report_filename)
@cli.option(--production, type=bool, default=False)
def tns_send(report_filename, production):
    tns_api_bulk_report.send_report(report_filename, production)


@cli.command()
@cli.argument(report_filename)
@cli.option(--production, type=bool, default=False)
def ctd_send(report_filename, production):
    with open(report_filename, 'r') as fp:
        dd = json.load(fp)

    dictin = dd  # TODO: extract relevant fields from TNS json for ctd

    caltechdata.send_ctd(dictin, production=production)

    
@cli.command()
@cli.argument(Id)
@cli.argument(filenames)
@cli.option(--production, type=bool, default=False)
def ctd_upload(Id, filenames, production):
    caltechdata.edit_ctd(Id, filenames=filenames, production=production)
