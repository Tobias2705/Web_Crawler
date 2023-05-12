import os
import sqlite3
import pandas as pd


class DataBaseManager:
    def __init__(self, db_path, clear_database=False):
        self.db_path = db_path
        self.clear_database = clear_database

    def create_db_create_tables(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            if self.clear_database:
                cur.execute("DROP TABLE IF EXISTS podmiot")
                cur.execute("DROP TABLE IF EXISTS jednostka_lokalna")
                cur.execute("DROP TABLE IF EXISTS reprezentant")
                cur.execute("DROP TABLE IF EXISTS infostrefa")
                cur.execute("DROP TABLE IF EXISTS konto")
                cur.execute("DROP TABLE IF EXISTS akcjonariusz")
                cur.execute("DROP TABLE IF EXISTS pkd")

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

            cur.close()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to initialize sqlite tables - {error}")

    def insert_entity_data(self):
        try:
            conn = sqlite3.connect(self.db_path)

            regon_entities_df = pd.read_csv('output/regon_entity_df', dtype={'regon': str, 'nip': str})
            regon_entities_df.to_sql('podmiot', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert entities into table podmiot - {error}")

    def insert_local_entity_data(self):
        try:
            conn = sqlite3.connect(self.db_path)

            local_regon_entities_df = pd.read_csv('output/regon_local_entity_df', dtype={'regon': str, 'nip': str})

            entities_ids = []
            for index, row in local_regon_entities_df.iterrows():
                query = "SELECT id FROM podmiot WHERE nip='{}'".format(row['nip j.nadrzędnej'])
                result = conn.execute(query).fetchall()
                if result:
                    entities_ids.append(result[0][0])
                else:
                    entities_ids.append(None)

            local_regon_entities_df.drop(columns=['regon j.nadrzędnej', 'nip j.nadrzędnej'], inplace=True)

            regon_entities = local_regon_entities_df.assign(id_jed_nadrzednej=entities_ids)
            regon_entities.to_sql('jednostka_lokalna', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert local entities into table jednostka_lokalna - {error}")

    def insert_general_entities_info(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            krs_general_df = pd.read_csv('output/krs_general_info_df', dtype={'regon': str, 'nip': str, 'krs': str})
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

    def insert_representatives_data(self):
        try:
            conn = sqlite3.connect(self.db_path)

            representatives_df = pd.read_csv('output/krs_representatives_df', dtype={'nip': str})

            entities_ids = []
            for index, row in representatives_df.iterrows():
                query = "SELECT id FROM podmiot WHERE nip='{}'".format(row['nip'])
                result = conn.execute(query).fetchall()
                if result:
                    entities_ids.append(result[0][0])
                else:
                    entities_ids.append(None)

            representatives_df.drop(columns=['nip'], inplace=True)

            representatives = representatives_df.assign(id_podmiotu=entities_ids)
            representatives.to_sql('reprezentant', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert representatives data into table reprezentant - {error}")

    def insert_infostrefa_posts(self):
        try:
            conn = sqlite3.connect(self.db_path)

            info_df = pd.read_csv('output/infostrefa_news_df', dtype={'nip': str})

            entities_ids = []
            for index, row in info_df.iterrows():
                query = "SELECT id FROM podmiot WHERE nip='{}'".format(row['nip'])
                result = conn.execute(query).fetchall()
                if result:
                    entities_ids.append(result[0][0])
                else:
                    entities_ids.append(None)

            info_df.drop(columns=['nip'], inplace=True)

            info = info_df.assign(id_podmiotu=entities_ids)
            info.to_sql('infostrefa', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert posts data into table infostrefa - {error}")

    def insert_shareholders_info(self):
        try:
            conn = sqlite3.connect(self.db_path)

            shareholders_df = pd.read_csv('output/aleo_shareholders_df', dtype={'nip': str})

            entities_ids = []
            for index, row in shareholders_df.iterrows():
                query = "SELECT id FROM podmiot WHERE nip='{}'".format(row['nip'])
                result = conn.execute(query).fetchall()
                if result:
                    entities_ids.append(result[0][0])
                else:
                    entities_ids.append(None)

            shareholders_df.drop(columns=['nip'], inplace=True)
            shareholders_df.rename(columns={'shareholder': 'nazwa'}, inplace=True)

            shareholders = shareholders_df.assign(id_podmiotu=entities_ids)
            shareholders.to_sql('akcjonariusz', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert shareholders data into table akcjonariusz - {error}")

    def insert_accounts_info(self):
        try:
            conn = sqlite3.connect(self.db_path)

            accounts_df = pd.read_csv('output/aleo_account_numbers_df', dtype={'nip': str})

            entities_ids = []
            for index, row in accounts_df.iterrows():
                query = "SELECT id FROM podmiot WHERE nip='{}'".format(row['nip'])
                result = conn.execute(query).fetchall()
                if result:
                    entities_ids.append(result[0][0])
                else:
                    entities_ids.append(None)

            accounts_df.drop(columns=['nip'], inplace=True)
            accounts_df.rename(columns={'account_number': 'numer'}, inplace=True)

            accounts = accounts_df.assign(id_podmiotu=entities_ids)
            accounts.to_sql('konto', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            print(f"Failed to insert bank accounts data into table konto - {error}")

    def select_from_db(self, table=''):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(f'SELECT * FROM {table}')
        results = cur.fetchall()

        for row in results:
            print(row)

        conn.close()


if __name__ == '__main__':
    path = os.getcwd() + "\\KNF_sentiment.db"
    db_manager = DataBaseManager(db_path=path, clear_database=True)

    # Initialize database
    db_manager.create_db_create_tables()

    # Insert entities data (from regon)
    db_manager.insert_entity_data()
    db_manager.insert_local_entity_data()

    # Insert additional entities data (from krs)
    db_manager.insert_general_entities_info()
    db_manager.insert_representatives_data()

    # Insert shareholders and bank accounts (from infostrefa)
    db_manager.insert_shareholders_info()
    db_manager.insert_accounts_info()

    # Insert posts data (from infostrefa)
    db_manager.insert_infostrefa_posts()

    db_manager.select_from_db(table='podmiot')
    db_manager.select_from_db(table='jednostka_lokalna')
    db_manager.select_from_db(table='reprezentant')
    db_manager.select_from_db(table='akcjonariusz')
    db_manager.select_from_db(table='konto')
    db_manager.select_from_db(table='infostrefa')
