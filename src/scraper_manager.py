from input_validator.input_validator import InputValidator
from aleo_scraper.AleoScrapper import get_href_links
from infostrefa_scrapper.infostrefa_scrapper import InfoStrefaScrapper
from krs_scraper.krs_scrapper import KrsScrapper
from regon_scraper.regon_scraper import RegonScraper

from threading import Thread
import pandas as pd
import os
import sqlite3

class ScraperManager:
    def __init__(self, input_path, log_scrap_info = False):
        data, errors = InputValidator(input_path).validate_input()
        self.log_scrap_info = log_scrap_info
        self.data = data

    def scrap(self):
        # run regon and krs scrapers parallelly
        regon_thread = Thread(target=self.run_regon_scraper)
        krs_thread = Thread(target=self.run_krs_scraper)

        print('Starting scraping regon and krs...')
        regon_thread.start()
        krs_thread.start()

        regon_thread.join()
        krs_thread.join()
        print('Stopped scraping regon and krs...')

        # run aleo and infostrefa parallelly
        aleo_thread = Thread(target=self.run_aleo_scraper)
        infostrefa_thread = Thread(target=self.run_infostrefa_scraper)

        print('Starting scraping infostrefa and aleo...')
        aleo_thread.start()
        infostrefa_thread.start()

        aleo_thread.join()
        infostrefa_thread.join()
        print('Stopped scraping infostrefa and aleo...')

    def run_aleo_scraper(self):
        #scraping from regon NIPs
        account_numbers_df = pd.DataFrame(columns = ['nip', 'account_number'])
        shareholders_df = pd.DataFrame(columns = ['nip', 'shareholder'])

        nips = self.regon_entity_df.nip.copy().drop_duplicates()

        for count, nip in enumerate(nips):
            counter = str(count+1) + '/' + str(len(nips))
            try:
                account_numbers, shareholders = get_href_links(nip)
                for account_number in account_numbers:
                    account_numbers_df.loc[len(account_numbers_df)] = [nip, account_number]
                
                for shareholder in shareholders:
                    shareholders_df.loc[len(shareholders_df)] = [nip, shareholder]

                if self.log_scrap_info:
                    print(f"{counter} AleoScraper scraped: {nip}")
            except:
                if self.log_scrap_info:
                    print(f"{counter} AleoScraper could not scrap: {nip}")

            
        self.aleo_account_numbers_df = account_numbers_df
        self.aleo_shareholders_df = shareholders_df

    def run_infostrefa_scraper(self):
        #scraping from regon NIPs and names
        entities_df = self.regon_entity_df[["nazwa", "nip"]].copy().drop_duplicates()
        scraper = InfoStrefaScrapper(entities_df, print_info=self.log_scrap_info)
        self.infostrefa_news_df = scraper.get_data()

    def run_krs_scraper(self):
        general_info_df = pd.DataFrame(columns=[
            "nazwa", "krs", "nip", "regon", "forma_prawna", "data_wpisu_do_rej_przeds", "data_wykr_z_rej_przeds",
            "nazwa_org_repr", "sposob_repr", "adr_www", "email"])
        representants_df = pd.DataFrame()

        scraper = KrsScrapper()

        for count, row in enumerate(self.data):    
            counter = str(count+1) + '/' + str(len(self.data))
            try:
                gen_info_dict, repr_df = scraper.scrap(row[0], row[1])

                representants_df = pd.concat([representants_df, repr_df], axis=0).reset_index(drop=True)
                general_info_df.loc[len(general_info_df)] = gen_info_dict.values()
                if self.log_scrap_info:
                    print(f"{counter} KrsScraper scraped: {row}")
            except:
                if self.log_scrap_info:
                    print(f"{counter} KrsScraper could not scrap: {row}")

        self.krs_representants_df = representants_df
        self.krs_general_info_df = general_info_df

    def run_regon_scraper(self):
        regon_entity_df = pd.DataFrame()
        regon_local_entity_df = pd.DataFrame()
        regon_pkd = pd.DataFrame()

        regon_scraper = RegonScraper()

        for count, row in enumerate(self.data):
            counter = str(count+1) + '/' + str(len(self.data))
            try:
                e_df, l_df, p_df = regon_scraper.get_entity_info(row[0], row[1])
                regon_entity_df = pd.concat([regon_entity_df, e_df], axis=0).reset_index(drop=True)
                regon_local_entity_df = pd.concat([regon_local_entity_df, l_df], axis=0).reset_index(drop=True)
                regon_pkd = pd.concat([regon_pkd, p_df], axis=0).reset_index(drop=True)
                if self.log_scrap_info:
                    print(f"{counter} RegonScrapper scraped: {row}")
            except:
                if self.log_scrap_info:
                    print(f"{counter} RegonScrapper could not scrap: {row}")

        self.regon_entity_df = regon_entity_df
        self.regon_local_entity_df = regon_local_entity_df
        self.regon_pkd_df = regon_pkd

    def get_results(self):
        results = {
            'regon_entity_df': self.regon_entity_df.copy(),
            'regon_local_entity_df': self.regon_local_entity_df.copy(),
            'regon_pkd_df': self.regon_pkd_df.copy(),
            'krs_representants_df': self.krs_representants_df.copy(),
            'krs_general_info_df': self.krs_general_info_df.copy(),
            'aleo_account_numbers_df': self.aleo_account_numbers_df.copy(),
            'aleo_shareholders_df': self.aleo_shareholders_df.copy(),
            'self.infostrefa_news_df': self.infostrefa_news_df.copy() 
        }
        return results

    def save_to_csv(self, path = ''):
        for k, v in self.get_results().items():
            v.to_csv(os.path.join(path, k), index=False)

    def create_db_create_tables(self, path):
        con = sqlite3.connect(path)
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS podmioty")
        cur.execute("DROP TABLE IF EXISTS reprezentanci")
        cur.execute("DROP TABLE IF EXISTS depeszeinfostrefy")
        cur.execute("DROP TABLE IF EXISTS kontabankowe")
        cur.execute("DROP TABLE IF EXISTS akcjonariusze")
        cur.execute("DROP TABLE IF EXISTS pkd")

        cur.execute("""
            CREATE TABLE podmioty(
                id INTEGER PRIMARY KEY,
                nip TEXT,
                nazwa TEXT,
                kod_i_nazwa_podstawowej_formy_prawnej TEXT,
                kod_i_nazwa_szczegolnej_formy_prawnej TEXT,
                kod_i_nazwa_formy_wlasnosci TEXT,
                data_wpisu_do_rejestru_przedsiebiorcow TEXT,
                data_wykreslenia_z_rejestru_przedsiebiorcow TEXT,
                adres_www TEXT,
                id_jednostki_nadrzednej INTEGER,
                jednostka_lokalna BOOLEAN,
                kraj TEXT,
                wojewodztwo TEXT,
                powiat TEXT,
                gmina TEXT,
                miejscowosc TEXT,
                ulica TEXT,
                nr TEXT,
                kod_pocztowy TEXT,
                FOREIGN KEY(id_jednostki_nadrzednej) REFERENCES podmioty(id)
            )
        """)
        
        cur.execute(""" 
            CREATE TABLE reprezentanci(
                id INTEGER PRIMARY KEY,
                id_podmiotu INTEGER,
                imie_pierwsze TEXT,
                imie_drugie TEXT,
                nazwisko TEXT,
                nazwisko_drugi_czlon TEXT,
                funkcja TEXT,
                FOREIGN KEY(id_podmiotu) REFERENCES podmioty(id)
            )
        """)

        cur.execute(""" 
            CREATE TABLE depeszeinfostrefy(
                id INTEGER PRIMARY KEY,
                id_podmiotu INTEGER,
                data TEXT,
                wiadomosc TEXT,
                FOREIGN KEY(id_podmiotu) REFERENCES podmioty(id)
            )
        """)

        cur.execute(""" 
            CREATE TABLE kontabankowe(
                id INTEGER PRIMARY KEY,
                numer TEXT,
                id_podmiotu INTEGER,
                FOREIGN KEY(id_podmiotu) REFERENCES podmioty(id)
            )
        """)

        cur.execute("""
            CREATE TABLE akcjonariusze(
                id INTEGER PRIMARY KEY,
                nazwa TEXT,
                id_podmiotu INTEGER,
                FOREIGN KEY(id_podmiotu) REFERENCES podmioty(id)
            )
        """)

        cur.execute("""
            CREATE TABLE pkd(
                id INTEGER PRIMARY KEY,
                kod TEXT,
                nazwa TEXT,
                id_podmiotu INTEGER,
                FOREIGN KEY(id_podmiotu) REFERENCES podmioty(id)
            )
        """)

if __name__ == '__main__':
    manager = ScraperManager('input.txt', log_scrap_info=True)
    # manager.scrap()
    # manager.save_to_csv(path='C:\\Users\\kaczm\\Documents\\sem1-tpd\\hurtownie\\Web_Crawler\\output')

    db_path = "C:\\Users\\kaczm\\Desktop\\osint.db"
    manager.create_db_create_tables(db_path)
    