import sys
import click
from PyQt5.QtWidgets import QApplication
import os
import pathlib

from WebCrawler.client.client_app import MainWindow
from WebCrawler.managers import DataBaseManager
from WebCrawler.managers import ScraperManager


@click.group()
def cli():
    pass


@click.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('-db', '--database', is_flag=True)
@click.option('-c', '--clear', is_flag=True)
def scrap(file, database, clear):
    scraper_manager = ScraperManager(os.path.abspath(file), log_scrap_info=True)
    scraper_manager.scrap()

    output_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', '..', '..', 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_dir = os.path.join(output_dir, 'csv')
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    scraper_manager.save_to_csv(path=csv_dir)

    if not database:
        return

    db_dir = os.path.join(output_dir, 'db')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    db_path = os.path.join(db_dir, 'KNF_sentiment.db')

    db_manager = DataBaseManager(db_path=db_path, clear_database=clear)
    db_manager.insert_all()


@click.command()
def gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


@click.command()
@click.option('-c', '--clear', is_flag=True)
def insert_to_db(clear):
    output_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', '..', '..', 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    db_dir = os.path.join(output_dir, 'db')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    db_path = os.path.join(db_dir, 'KNF_sentiment.db')

    db_manager = DataBaseManager(db_path=db_path, clear_database=clear)
    db_manager.insert_all()


@click.command()
@click.argument('id', required=True)
@click.argument('id_type', required=True)
def krs(id, id_type):
    click.echo("Checking KRS...")

    try:
        from WebCrawler.scrapers import KrsScrapper
        krs_scrapper = KrsScrapper(id, id_type)
        general_info, representants = krs_scrapper.scrap()

        click.echo(f"{'Nazwa: ':<40}{general_info['nazwa']}")
        click.echo(f"{'KRS: ':<40}{general_info['krs']}")
        click.echo(f"{'NIP: ':<40}{general_info['nip']}")
        click.echo(f"{'Regon: ':<40}{general_info['regon']}")
        click.echo(f"{'Forma prawna: ':<40}{general_info['forma_prawna']}")
        click.echo(f"{'Data wpisu do Rej. Przeds.: ':<40}{general_info['data_wpisu_do_rej_przeds']}")
        click.echo(f"{'Data wykr. z Rej. Przed.:  ':<40}{general_info['data_wykr_z_rej_przeds']}")
        click.echo(f"{'Adres www: ':<40}{general_info['adr_www']}")
        click.echo(f"{'Email: ':<40}{general_info['email']}")
        import pandas as pd
        representants.drop(columns=['nip'], inplace=True)
        click.echo("\nZarząd: ")
        click.echo(representants.to_string())
    except:
        click.echo("Couldn't scrap this entity.")



cli.add_command(scrap)
cli.add_command(gui)
cli.add_command(insert_to_db)
cli.add_command(krs)

if __name__ == "__main__":
    cli()
