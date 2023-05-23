"""
database_manager.py
====================================
This module is used to create database using scraped data.
"""

import os
import sqlite3
import pandas as pd
import pathlib
from typing import List


class DataBaseManager:
    """
        This class is used to create a database using scraped data from all scrapers modules.
        It is initialised with the following parameters.

        Attributes:
            db_path (str): Contains the path to the database file (.db).
            clear_database (bool): Optional parameter that specifies whether the database tables are deleted at runtime.
    """

    def __init__(self, db_path, clear_database=False):
        """
            Initializes the RegonScraper class.
        """
        self.db_path = db_path
        self.clear_database = clear_database
        self.output_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'output')

    @staticmethod
    def _find_entities(conn: sqlite3.Connection, df: pd.DataFrame, table: str, column: str, compare: str) -> List[int]:
        """
            Private static method used to finding entity identifiers to create relationships between tables in
            the database.

            :param conn: A `sqlite3.Connection` object representing the connection to the database.
            :param df: A Pandas `DataFrame` object representing the data to be searched for entity identifiers.
            :param table: A string representing the name of the table to search for entity identifiers.
            :param column: A string representing the name of the column in the `df` DataFrame to compare with
                           the values in the database table.
            :param compare: A string representing the column to compare with the values in the database table.
            :return: A list of entity identifiers for each row in the `df` DataFrame.
                     If an entity is not found, the corresponding value in the list will be `None`.
        """
        entities_ids = []
        for index, row in df.iterrows():
            query = f"SELECT id FROM {table} WHERE {compare}='{row[column]}'"
            result = conn.execute(query).fetchall()
            if result:
                entities_ids.append(result[0][0])
            else:
                entities_ids.append(None)

        return entities_ids

    @staticmethod
    def _find_times(conn: sqlite3.Connection, df: pd.DataFrame) -> List[int]:
        """
            Private static method used to finding entity identifiers to create relationships between tables in
            the database.

            :param conn: A `sqlite3.Connection` object representing the connection to the database.
            :param df: A Pandas `DataFrame` object representing the data to be searched for times identifiers.
            :return: A list of time identifiers for each row in the `df` DataFrame.
                     If an entity is not found, the corresponding value in the list will be `None`.
        """
        times_ids = []
        for index, row in df.iterrows():
            timestamp = pd.to_datetime(row['timestamp'], format='%Y-%m-%d %H:%M:%S')
            query = f"SELECT id FROM czas WHERE godzina='{timestamp.hour}' AND dzien='{timestamp.day}'" \
                    f"AND miesiac='{timestamp.month}' AND rok='{timestamp.year}'"

            result = conn.execute(query).fetchall()
            if result:
                times_ids.append(result[0][0])
            else:
                times_ids.append(None)

        return times_ids

    def _create_db_create_tables(self) -> None:
        """
            Public method used to create tables in database.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            if self.clear_database:
                cur.execute("DROP TABLE IF EXISTS podmiot")
                cur.execute("DROP TABLE IF EXISTS jednostka_lokalna")
                cur.execute("DROP TABLE IF EXISTS reprezentant")
                cur.execute("DROP TABLE IF EXISTS infostrefa")
                cur.execute("DROP TABLE IF EXISTS bankier")
                cur.execute("DROP TABLE IF EXISTS konto")
                cur.execute("DROP TABLE IF EXISTS akcjonariusz")
                cur.execute("DROP TABLE IF EXISTS pkd")
                cur.execute("DROP TABLE IF EXISTS czas")
                cur.execute("DROP TABLE IF EXISTS ocena")

            # entity dimension
            cur.execute("""
                CREATE TABLE IF NOT EXISTS podmiot(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    regon TEXT,
                    nip TEXT,
                    nazwa TEXT,
                    forma_prawna TEXT,
                    sz_forma_prawna TEXT,
                    forma_wlasnosci TEXT,
                    data_wpisu TEXT,
                    data_wykreslenia TEXT,
                    adres_www TEXT,
                    kraj TEXT,
                    wojewodztwo TEXT,
                    powiat TEXT,
                    gmina TEXT,
                    miejscowosc TEXT,
                    ulica TEXT,
                    nr TEXT,
                    kod_pocztowy TEXT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS jednostka_lokalna(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_jed_nadrzednej INTEGER,
                    regon TEXT,
                    nazwa TEXT,
                    forma_prawna TEXT,
                    sz_forma_prawna TEXT,
                    forma_wlasnosci TEXT,
                    kraj TEXT,
                    wojewodztwo TEXT,
                    powiat TEXT,
                    gmina TEXT,
                    miejscowosc TEXT,
                    ulica TEXT,
                    nr TEXT,
                    kod_pocztowy TEXT,
                    FOREIGN KEY(id_jed_nadrzednej) REFERENCES podmiot(id)
                )
            """)

            cur.execute(""" 
                CREATE TABLE IF NOT EXISTS reprezentant(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_podmiotu INTEGER,
                    imie TEXT,
                    imie2 TEXT,
                    nazwisko TEXT,
                    nazwisko2 TEXT,
                    funkcja TEXT,
                    FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
                )
            """)

            cur.execute(""" 
                CREATE TABLE IF NOT EXISTS infostrefa(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_podmiotu INTEGER,
                    data TEXT,
                    wiadomosc TEXT,
                    FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
                )
            """)

            cur.execute(""" 
                CREATE TABLE IF NOT EXISTS bankier(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_podmiotu INTEGER,
                    data TEXT,
                    wiadomosc TEXT,
                    FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
                )
            """)

            cur.execute(""" 
                CREATE TABLE IF NOT EXISTS konto(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_podmiotu INTEGER,
                    numer TEXT,
                    FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS akcjonariusz(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_podmiotu INTEGER,
                    nazwa TEXT,
                    FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS pkd(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_podmiotu INTEGER,
                    kod TEXT,
                    nazwa TEXT,
                    FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
                )
            """)

            # time dimension
            cur.execute("""
                CREATE TABLE IF NOT EXISTS czas(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    godzina INTEGER,
                    dzien INTEGER,
                    miesiac INTEGER,
                    rok INTEGER
                )
            """)

            # fact evaluation
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ocena(
                    id_czasu INTEGER,
                    id_podmiotu INTEGER,
                    typ_oceny TEXT,
                    FOREIGN KEY(id_czasu) REFERENCES czas(id),
                    FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
                )
            """)

            cur.close()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to initialize sqlite tables - {error}")

    def _insert_entity_data(self) -> None:
        """
            Public method used to complete the 'entity' table with the data (from regon) of the scraped entities.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            regon_entities_df = pd.read_csv(f'{self.output_dir}/regon_entity_df', dtype={'regon': str, 'nip': str})
            regon_entities_df.drop(columns=['nazwa_gieldowa'], inplace=True)
            regon_entities_df.to_sql('podmiot', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert entities into table podmiot - {error}")

    def _insert_local_entity_data(self) -> None:
        """
            Public method used to complete the 'local entity' table with the data (from regon)
            of the scraped local entities.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            local_regon_entities_df = pd.read_csv(f'{self.output_dir}/regon_local_entity_df',
                                                  dtype={'regon': str, 'nip': str})

            entities_ids = self._find_entities(conn, local_regon_entities_df, 'podmiot', 'nip j.nadrzędnej', 'nip')

            local_regon_entities_df.drop(columns=['regon j.nadrzędnej', 'nip j.nadrzędnej'], inplace=True)

            regon_entities = local_regon_entities_df.assign(id_jed_nadrzednej=entities_ids)
            regon_entities.to_sql('jednostka_lokalna', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert local entities into table jednostka_lokalna - {error}")

    def _insert_general_entities_info(self) -> None:
        """
            Public method used to update the 'entity' table with the additional data (from krs) of the scraped entities.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            krs_general_df = pd.read_csv(f'{self.output_dir}/krs_general_info_df',
                                         dtype={'regon': str, 'nip': str, 'krs': str})
            for index, row in krs_general_df.iterrows():
                nip = row['nip']
                query = "SELECT id FROM podmiot WHERE nip='{}'".format(nip)
                result = conn.execute(query).fetchone()
                if result:
                    general_info = krs_general_df.loc[krs_general_df['nip'] == nip]
                    update_query = """UPDATE podmiot SET data_wpisu=?, data_wykreslenia=?, adres_www=? WHERE id=?"""
                    values = (general_info['data_wpisu_do_rej_przeds'].values[0],
                              general_info['data_wykr_z_rej_przeds'].values[0],
                              general_info['adr_www'].values[0], str(result[0]))
                    cur.execute(update_query, values)
                    conn.commit()

            cur.close()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert additional entities data into table podmiot - {error}")

    def _insert_representatives_data(self) -> None:
        """
            Public method used to complete the 'representative' table with the data (from krs) of the scraped entities.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            representatives_df = pd.read_csv(f'{self.output_dir}/krs_representatives_df', dtype={'nip': str})

            entities_ids = self._find_entities(conn, representatives_df, 'podmiot', 'nip', 'nip')

            representatives_df.drop(columns=['nip'], inplace=True)

            representatives = representatives_df.assign(id_podmiotu=entities_ids)
            representatives.to_sql('reprezentant', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert representatives data into table reprezentant - {error}")

    def _insert_infostrefa_posts(self) -> None:
        """
            Public method used to complete the 'ifnostrefa' table with the data of the scraped messages
            about entities.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            info_df = pd.read_csv(f'{self.output_dir}/infostrefa_news_df', dtype={'nip': str})

            entities_ids = self._find_entities(conn, info_df, 'podmiot', 'nip', 'nip')

            info_df.drop(columns=['nip'], inplace=True)

            info = info_df.assign(id_podmiotu=entities_ids)
            info.to_sql('infostrefa', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert posts data into tables infostrefa & bankier - {error}")

    def _insert_bankier_posts(self) -> None:
        """
            Public method used to complete the 'bankier' table with the data of the scraped messages
            about entities.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            bank_df = pd.read_csv(f'{self.output_dir}/bankier_news_df', dtype={'nip': str})

            entities_ids = self._find_entities(conn, bank_df, 'podmiot', 'nip', 'nip')

            bank_df.drop(columns=['nip'], inplace=True)

            bank = bank_df.assign(id_podmiotu=entities_ids)
            bank.to_sql('bankier', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert posts data into table bankier - {error}")

    def _insert_shareholders_info(self) -> None:
        """
            Public method used to complete the 'shareholder' table with the data (from aleo) of the scraped entities.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            shareholders_df = pd.read_csv(f'{self.output_dir}/aleo_shareholders_df', dtype={'nip': str})

            entities_ids = self._find_entities(conn, shareholders_df, 'podmiot', 'nip', 'nip')

            shareholders_df.drop(columns=['nip'], inplace=True)
            shareholders_df.rename(columns={'shareholder': 'nazwa'}, inplace=True)

            shareholders = shareholders_df.assign(id_podmiotu=entities_ids)
            shareholders.to_sql('akcjonariusz', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert shareholders data into table akcjonariusz - {error}")

    def _insert_accounts_info(self) -> None:
        """
            Public method used to complete the 'account' table with the data (from aleo) of the scraped entities.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            accounts_df = pd.read_csv(f'{self.output_dir}/aleo_account_numbers_df', dtype={'nip': str})

            entities_ids = self._find_entities(conn, accounts_df, 'podmiot', 'nip', 'nip')

            accounts_df.drop(columns=['nip'], inplace=True)
            accounts_df.rename(columns={'account_number': 'numer'}, inplace=True)

            accounts = accounts_df.assign(id_podmiotu=entities_ids)
            accounts.to_sql('konto', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert bank accounts data into table konto - {error}")

    def _insert_pkd_info(self) -> None:
        """
            Public method used to complete the 'pkd' table with the data (from regon) of the scraped entities.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            pkd_df = pd.read_csv(f'{self.output_dir}/regon_pkd_df', dtype={'regon': str})

            entities_ids = []
            for index, row in pkd_df.iterrows():
                regon = row['regon']
                if len(regon) == 14:
                    query = "SELECT id FROM jednostka_lokalna WHERE regon='{}'".format(row['regon'])
                else:
                    query = "SELECT id FROM podmiot WHERE regon='{}'".format(row['regon'])
                result = conn.execute(query).fetchall()
                if result:
                    entities_ids.append(result[0][0])
                else:
                    entities_ids.append(None)

            pkd_df.drop(columns=['regon'], inplace=True)

            pkd = pkd_df.assign(id_podmiotu=entities_ids)
            pkd.to_sql('pkd', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert pkd data into table pkd - {error}")

    def _insert_times_info(self) -> None:
        """
            Public method used to complete the 'time' table with the data of the scraped forums.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            times_df = pd.read_csv(f'{self.output_dir}/time_df')
            times_df.drop(columns=['timestamp'], inplace=True) # do wyjebania przed commitem
            times_df.drop_duplicates(inplace=True)
            times_df.to_sql('czas', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert time data into table czas - {error}")

    def _insert_analysis_info_data(self) -> None:
        """
            Public method used to complete the 'evaluation' table with the results from the analysis of the
            infostrefa and bankier entries.

            :param: None.
            :return: None.
        """
        try:
            conn = sqlite3.connect(self.db_path)

            # Infostrefa
            sentiment_info_df = pd.read_csv(f'{self.output_dir}/sentiment_info_df', dtype={'nip': str})

            entities_ids = self._find_entities(conn, sentiment_info_df, 'podmiot', 'nip', 'nip')
            times_ids = self._find_times(conn, sentiment_info_df)

            sentiment_info_df.drop(columns=['nip'], inplace=True)
            sentiment_info_df.drop(columns=['timestamp'], inplace=True)

            sentiment = sentiment_info_df.assign(id_podmiotu=entities_ids, id_czasu=times_ids)
            sentiment.to_sql('ocena', conn, if_exists='append', index=False)

            conn.commit()

            # Bankier
            # bankier_info_df = pd.read_csv(f'{self.output_dir}/sentiment_bankier_df', dtype={'nip': str})
            #
            # entities_ids = self._find_entities(conn, bankier_info_df, 'podmiot', 'nip', 'nip')
            # times_ids = self._find_times(conn, bankier_info_df)
            #
            # bankier_info_df.drop(columns=['nip'], inplace=True)
            # bankier_info_df.drop(columns=['timestamp'], inplace=True)
            #
            # sentiment = bankier_info_df.assign(id_podmiotu=entities_ids, id_czasu=times_ids)
            # sentiment.to_sql('ocena', conn, if_exists='append', index=False)
            #
            # conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert time data into table czas - {error}")

    def insert_all(self):
        # Initialize database
        self._create_db_create_tables()

        # Initialize time data
        self._insert_times_info()

        # Insert entities data (from regon)
        self._insert_entity_data()
        self._insert_local_entity_data()
        self._insert_pkd_info()

        # Insert additional entities data (from krs)
        self._insert_general_entities_info()
        self._insert_representatives_data()

        # Insert shareholders and bank accounts (from infostrefa)
        self._insert_shareholders_info()
        self._insert_accounts_info()

        # Insert posts data (from infostrefa and bankier)
        self._insert_infostrefa_posts()
        self._insert_bankier_posts()

        # Insert results of sentiment analysis
        self._insert_analysis_info_data()


if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'database')) + "\\KNF_sentiment.db"
    db_manager = DataBaseManager(db_path=path, clear_database=True)
    db_manager.insert_all()
