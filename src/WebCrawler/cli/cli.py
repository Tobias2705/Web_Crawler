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
@click.option('-db', '--database', is_flag=True, help='Specifies whether results should be saved to a database.')
@click.option('-c', '--clear', is_flag=True, help='Specifies whether to clean a database before saving results there.')
def scrap(file, database, clear):
    """Runs the whole process of scraping and doing sentiment analysis.

    FILE is the path to the file with entities to scrap.
    """
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
    """Runs the app with a GUI.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


@click.command()
@click.option('-c', '--clear', is_flag=True, help='Specifies whether to clean a database before saving results there.')
def insert_to_db(clear):
    """Saves results of scraping to the database.
    """
    output_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', '..', '..', 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    db_dir = os.path.join(output_dir, 'db')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    db_path = os.path.join(db_dir, 'KNF_sentiment.db')

    db_manager = DataBaseManager(db_path=db_path, clear_database=clear)
    db_manager.insert_all()
    click.echo("Data inserted")



@click.command()
@click.argument('entity_id', required=True)
@click.argument('id_type', required=True)
def check_info(entity_id, id_type):
    """Allows to check some basic info about the entity from regon and krs.

    ENTITY_ID specifies the identifier of the entity.
    
    ID_TYPE specifies the the of given identifier (NIP, REGON or KRS).
    """
    click.echo("Checking information about entity...")

    try:
        from WebCrawler.scrapers import KrsScrapper, RegonScraper
        regon_scraper = RegonScraper()
        _, local_entities_df, pkd_df = regon_scraper.get_entity_info(entity_id, id_type)

        krs_scrapper = KrsScrapper(entity_id, id_type)
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
        if not representants.empty:
            click.echo("\nZarząd: ")
            representants.drop(columns=['nip'], inplace=True)
            click.echo(representants.to_string())
        if not local_entities_df.empty:
            local_entities_df = local_entities_df[['regon', 'nazwa']]
            click.echo("\nJednostki lokalne: ")
            click.echo(local_entities_df.to_string())
        if not pkd_df.empty:
            click.echo("\nPKD: ")
            pkd_df.drop(columns=['regon'], inplace=True)
            click.echo(pkd_df.to_string())
    except:
        click.echo("Couldn't scrap this entity.")


cli.add_command(scrap)
cli.add_command(gui)
cli.add_command(insert_to_db)
cli.add_command(check_info)

if __name__ == "__main__":
    cli()
