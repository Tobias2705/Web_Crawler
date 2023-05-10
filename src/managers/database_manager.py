import os
import sqlite3
import numpy as np
import pandas as pd


class DataBaseManager:
    def __init__(self, clear_database=False, log_info=False):
        self.clear_database = clear_database
        self.log_info = log_info

    def create_db_create_tables(self, path):
        conn = sqlite3.connect(path)
        cur = conn.cursor()

        if self.clear_database:
            cur.execute("DROP TABLE IF EXISTS podmiot")
            cur.execute("DROP TABLE IF EXISTS adres")
            cur.execute("DROP TABLE IF EXISTS reprezentant")
            cur.execute("DROP TABLE IF EXISTS infostrefa")
            cur.execute("DROP TABLE IF EXISTS konto")
            cur.execute("DROP TABLE IF EXISTS akcjonariusz")
            cur.execute("DROP TABLE IF EXISTS pkd")
            if self.log_info:
                print('Tables dropped')

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
                id_jed_nadrzednej INTEGER,
                jed_lokalna BOOLEAN
            )
        """)
        if self.log_info:
            print('Podmiot table created')

        cur.execute("""
            CREATE TABLE IF NOT EXISTS adres(
                id_podmiotu INTEGER
                kraj TEXT,
                wojewodztwo TEXT,
                powiat TEXT,
                gmina TEXT,
                miejscowosc TEXT,
                ulica TEXT,
                nr TEXT,
                kod_pocztowy TEXT,
                FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
            )
        """)
        if self.log_info:
            print('Adres table created...')

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
        if self.log_info:
            print('Reprezentant table created')

        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS infostrefa(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_podmiotu INTEGER,
                data TEXT,
                wiadomosc TEXT,
                FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
            )
        """)
        if self.log_info:
            print('Infostrefa table created')

        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS konto(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_podmiotu INTEGER,
                numer TEXT,
                FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
            )
        """)
        if self.log_info:
            print('Konto table created')

        cur.execute("""
            CREATE TABLE IF NOT EXISTS akcjonariusz(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_podmiotu INTEGER,
                nazwa TEXT,
                FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
            )
        """)
        if self.log_info:
            print('Akcjonariusz table created')

        cur.execute("""
            CREATE TABLE IF NOT EXISTS IDpkd(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_podmiotu INTEGER,
                kod TEXT,
                nazwa TEXT,
                FOREIGN KEY(id_podmiotu) REFERENCES podmiot(id)
            )
        """)
        if self.log_info:
            print('PKD table created')

        conn.close()

    def insert_entity_data(self, path):
        conn = sqlite3.connect(path)

        regon_entities = pd.read_csv('output/regon_entity_df', dtype={'regon': str, 'nip': str})
        regon_entities = regon_entities.iloc[:, :6]

        regon_entities = regon_entities.assign(data_wpisu=None, data_wykreslenia=None, adres_www=None,
                                               id_jed_nadrzednej=None, jed_lokalna=False)

        regon_entities.to_sql('podmiot', conn, if_exists='append', index=False)

        conn.commit()
        conn.close()

    def insert_local_entity_data(self, path):
        conn = sqlite3.connect(path)

        local_regon_entities = pd.read_csv('output/regon_local_entity_df')
        local_regon_entities = local_regon_entities.iloc[:, :6]
        entities_ids = []
        for index, row in local_regon_entities.iterrows():
            query = "SELECT id FROM podmiot WHERE nip='{}'".format(row['nip j.nadrzędnej'])
            result = conn.execute(query).fetchall()
            if result:
                entities_ids.append(result[0][0])
            else:
                entities_ids.append(None)

        regon_entities = local_regon_entities.assign(data_wpisu=None, data_wykreslenia=None, adres_www=None,
                                                     id_jed_nadrzednej=entities_ids, jed_lokalna=True)
        regon_entities.to_sql('podmiot', conn, if_exists='append', index=False)

        conn.commit()
        conn.close()


if __name__ == '__main__':
    db_manager = DataBaseManager(clear_database=True, log_info=True)
    db_path = os.getcwd() + "\\osint.db"

    db_manager.create_db_create_tables(db_path)
    db_manager.insert_entity_data(db_path)
    #db_manager.insert_local_entity_data(db_path)
