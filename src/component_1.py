"""
component_1.py
====================================
This module is used to scrape information from the REGON database.
"""

import re
import pandas as pd
from typing import Union, Tuple, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def check_nip_regon_krs(value: str) -> Union[str, None]:
    """
    Check whether a given string is a valid NIP, REGON, or KRS number.

    :param value: The string to be checked.
    :return: The type of the number if it is valid (NIP, REGON, or KRS), or None if it is not a valid identifier.
    """
    if len(value) == 10 and re.match(r'^\d{10}$', value):
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(value[i]) * weights[i] for i in range(9)) % 11
        if checksum == int(value[9]):
            return 'NIP'
    elif len(value) in [9, 14] and re.match(r'^\d+$', value):
        if len(value) == 9:
            value = f"0{value}"
        weights_9 = [8, 9, 2, 3, 4, 5, 6, 7]
        weights_14 = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
        weights = weights_14 if len(value) == 14 else weights_9
        checksum = sum(int(value[i]) * weights[i] for i in range(len(weights))) % 11
        if len(value) == 14:
            return 'REGON' if checksum % 10 == int(value[-1]) else None
        else:
            return 'NIP' if checksum == int(value[-1]) else 'REGON'
    elif len(value) == 10 and re.match(r'^\d{10}$', value):
        return 'KRS'

    return None


class RegonDatabaseScrapper:
    """
    This class is used to create a scrapper that scrapes information about entities from the REGON database.
    It is initialised with the following parameters

    Args:
        filepath (str): The path to the file from which the data will be loaded.

    Attributes:
        filepath (str): The path to the file from which the data will be loaded.
        entity_data (pandas.DataFrame): The DataFrame where the scraped data about entities will be stored.
        local_entity_data (pandas.DataFrame): The DataFrame where the scraped data about local entities will be stored.
        key_type (dict): The dictionary containing the keys and their corresponding identifiers used for crawling.
        entity_type (dict): The dictionary containing the entity types and their corresponding identifiers used
                            for scarping.
        local_entity_type (dict): The dictionary containing the local entity types and their corresponding identifiers
                            used for scarping.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.entity_data = pd.DataFrame(columns=[
            'regon',
            'nip',
            'nazwa',
            'kod_i_nazwa_podstawowej_formy_prawnej',
            'kod_i_nazwa_szczegolnej_formy_prawnej',
            'kod_i_nazwa_formy_wlasnosci',
            'kraj',
            'wojewodztwo',
            'powiat',
            'gmina',
            'miejscowosc',
            'ulica',
            'nr_nieruchomosci',
            'kod_pocztowy'
        ])
        self.local_entity_data = pd.DataFrame(columns=[
            'regon',
            'regon j.nadrzędnej',
            'nip j.nadrzędnej',
            'nazwa',
            'kraj',
            'wojewodztwo',
            'powiat',
            'gmina',
            'miejscowosc',
            'ulica',
            'nr_nieruchomosci',
            'kod_pocztowy'
        ])
        self.key_type = {
            'NIP': 'txtNip',
            'REGON': 'txtRegon',
            'KRS': 'txtKrs'
        }
        self.entity_type = {
            'tblRaportJFizyczna': 'fiz',
            'tblRaportJPrawna': 'praw',
            'tblRaportJLokalnaPrawnej': 'lokpraw',
            'tblRaportJLokalnaFizycznej': 'lokfiz'
        }
        self.local_entity_type = {
            'praw_lokTable': 'praw_lok',
            'fiz_lokTable': 'fiz_lok',
            'lokpraw': 'praw',
            'lokfiz': 'fiz'
        }

    def _identify_entity_type(self, driver: webdriver) -> Union[str, None]:
        """
            Private method used to identify the type of the entity in the database.

            :param driver: The webdriver object used to scrape the data.
            :return: The entity type identifier as a string.
        """
        for entity_id, entity_type in self.entity_type.items():
            if 'block' in driver.find_element(By.ID, entity_id).get_attribute('style'):
                return entity_type
        return None

    def _identify_local_entity_type(self, driver: webdriver) -> Union[str, None]:
        """
            Private method used to identify the type of the local entity in the database.

            :param driver: The webdriver object used to scrape the data.
            :return: The local entity type identifier as a string.
        """
        for l_entity_id, l_entity_type in self.local_entity_type.items():
            if 'table' in driver.find_element(By.ID, l_entity_id).get_attribute('style'):
                return l_entity_type
        return None

    def _get_data(self, key_value: str, idx: int) -> Tuple[int, List[str]]:
        """
            Private method used to scrape the data from the database.

            :param key_value: The key value used to search for the entity in the database.
            :param idx: Value specifying the number of the line to be analysed.
            :return: Number of entities identifying themselves with a given key and the list of local entities regons.
        """
        url = "https://wyszukiwarkaregon.stat.gov.pl/appBIR/index.aspx"
        data_type = check_nip_regon_krs(key_value)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        driver.get(url)
        input_data = driver.find_element(By.ID, self.key_type[data_type])
        # input_data = WebDriverWait(driver, 10).until(
        #     ec.presence_of_element_located((By.ID, self.key_type[data_type])))
        input_data.send_keys(str(key_value))

        submit_button = driver.find_element(By.ID, "btnSzukaj")
        submit_button.click()

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'tabelaZbiorczaListaJednostek')))

        table_body = driver.find_element(By.CLASS_NAME, 'tabelaZbiorczaListaJednostek').find_element(By.TAG_NAME,
                                                                                                     'tbody')
        rows = table_body.find_elements(By.TAG_NAME, 'tr')

        regon_link = rows[idx].find_element(By.TAG_NAME, 'a')
        regon_link.click()

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'tabelaRaportWewn')))

        entity_type = self._identify_entity_type(driver)

        self._get_entity_details(driver, entity_type)

        local_regons = self._check_if_local_entities_exist(driver, entity_type)
        driver.quit()

        return len(rows), local_regons

    def _get_entity_details(self, driver: webdriver, entity_type) -> None:
        """
            Private method used to extract the entity details from the scraped page.

            :param driver: The webdriver object used to scrape the data.
            :param entity_type: The local entity type identifier as a string.
            :return: None.
        """
        row_data = []

        if entity_type in ['fiz', 'praw']:
            # REGON
            row_data.append(driver.find_element(By.ID, f'{entity_type}_regon9').text)
            # NIP
            row_data.append(driver.find_element(By.ID, f'{entity_type}_nip').text)
            # NAZWA
            row_data.append(driver.find_element(By.ID, f'{entity_type}_nazwa').text)
            # kod i nazwa podstawowej formy prawnej
            row_data.append(driver.find_element(By.ID, f'{entity_type}_nazwaPodstawowejFormyPrawnej').text)
            # kod i nazwa szczególnej formy prawnej
            row_data.append(driver.find_element(By.ID, f'{entity_type}_nazwaSzczegolnejFormyPrawnej').text)
            # kod i nazwa formy własności
            row_data.append(driver.find_element(By.ID, f'{entity_type}_nazwaFormyWlasnosci').text)
            # kraj
            row_data.append(driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaKraju').text)
            # województwo
            row_data.append(driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaWojewodztwa').text)
            # powiat
            row_data.append(driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaPowiatu').text)
            # gmina
            row_data.append(driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaGminy').text)
            # miejscowość
            row_data.append(driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaMiejscowosci').text)
            # ulica
            row_data.append(driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaUlicy').text)
            # nr nieruchomości
            row_data.append(driver.find_element(By.ID, f'{entity_type}_adSiedzNumerNieruchomosci').text)
            # kod pocztowy
            row_data.append(driver.find_element(By.ID, f'{entity_type}_adSiedzKodPocztowy').text)

            self.entity_data.loc[len(self.entity_data)] = row_data
        elif entity_type in ['lokpraw', 'lokfiz']:
            self._get_local_entity_details(driver, entity_type)

    def _get_local_entity_details(self, driver: webdriver, entity_type: str) -> None:
        """
            Private method used to extract the local entity details from the scraped page.

            :param driver: The webdriver object used to scrape the data.
            :param entity_type: The local entity type identifier as a string.
            :return: None.
        """
        row_data = [driver.find_element(By.ID, f'{entity_type}_regon14').text,
                    driver.find_element(By.ID, f'{entity_type}_{self.local_entity_type[entity_type]}_regon').text,
                    driver.find_element(By.ID, f'{entity_type}_{self.local_entity_type[entity_type]}_nip').text,
                    driver.find_element(By.ID, f'{entity_type}_nazwa').text,
                    driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaKraju').text,
                    driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaWojewodztwa').text,
                    driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaPowiatu').text,
                    driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaGminy').text,
                    driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaMiejscowosci').text,
                    driver.find_element(By.ID, f'{entity_type}_adSiedzNazwaUlicy').text,
                    driver.find_element(By.ID, f'{entity_type}_adSiedzNumerNieruchomosci').text,
                    driver.find_element(By.ID, f'{entity_type}_adSiedzKodPocztowy').text]

        self.local_entity_data.loc[len(self.local_entity_data)] = row_data

    def _check_if_local_entities_exist(self, driver: webdriver, entity_type) -> List[str]:
        """
            Private method used to check if local entities exist.

            :param driver: The webdriver object used to scrape the data.
            :param entity_type: The local entity type identifier as a string.
            :return: None.
        """
        local_regons = []
        if entity_type in ['fiz', 'praw']:
            if 'table' in driver.find_element(By.ID, f'{entity_type}_lokTable').get_attribute('style'):
                list_button = driver.find_element(By.ID, f'{entity_type}_butLinkLok')
                list_button.click()
                WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, f'{entity_type}_lok')))
                td = driver.find_element(By.ID, f'{entity_type}_lok')
                body = td.find_element(By.TAG_NAME, 'tbody')
                rows = body.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    local_regons.append(row.find_element(By.TAG_NAME, 'a').text)
        return local_regons


    def get_entity_info(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
            Public method used to scrape the data from the database and return it as a pandas DataFrame.

            :param: None.
            :return: The scraped data as a pandas DataFrame.
        """
        with open(self.filepath, 'r') as f:
            for line in f:
                rows_num, local_regons = self._get_data(line.strip(), 0)
                for regon in local_regons:
                    self._get_data(regon.strip(), 0)
                for idx in range(1, rows_num):
                    _, local_regons = self._get_data(line.strip(), idx)
                    for regon in local_regons:
                        self._get_data(regon.strip(), 0)

        return self.entity_data, self.local_entity_data
