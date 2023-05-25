import sys
import click
from PyQt5.QtWidgets import QApplication
import os
import pathlib

from src.client.client_app import MainWindow
from src.managers.database_manager import DataBaseManager
from src.managers.scraper_manager import ScraperManager


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

    csv_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'components', 'managers', 'output')
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    scraper_manager.save_to_csv(path=csv_dir)

    if not database:
        return

    db_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    db_manager = DataBaseManager(db_path=os.path.join(db_dir, 'KNF_sentiment.db'), clear_database=clear)
    db_manager.insert_all()



@click.command()
def gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


cli.add_command(scrap)
cli.add_command(gui)

if __name__ == "__main__":
    cli()
