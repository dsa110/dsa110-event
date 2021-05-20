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
    caltechdata.(report_filename)
