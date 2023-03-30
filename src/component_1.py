"""
component_1.py
====================================
This module is used to scrape information from the REGON database.
"""

import re
import pandas as pd
from typing import Union
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
        weights_9 = [8, 9, 2, 3, 4, 5, 6, 7]
        weights_14 = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
        weights = weights_14 if len(value) == 14 else weights_9
        checksum = sum(int(value[i]) * weights[i] for i in range(len(weights))) % 11
        if checksum == int(value[-1]):
            return 'REGON'
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
        data (pandas.DataFrame): The DataFrame where the scraped data will be stored.
        key_type (dict): The dictionary containing the keys and their corresponding identifiers used for crawling.
        entity_type (dict): The dictionary containing the entity types and their corresponding identifiers used
                            for scarping.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = pd.DataFrame(columns=[
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

    def _get_data(self, key_value: str) -> None:
        """
            Private method used to scrape the data from the database.

            :param key_value: The key value used to search for the entity in the database.
            :return: None.
        """
        url = "https://wyszukiwarkaregon.stat.gov.pl/appBIR/index.aspx"
        data_type = check_nip_regon_krs(key_value)
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        input_data = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, self.key_type[data_type])))
        input_data.send_keys(str(key_value))

        submit_button = driver.find_element(By.ID, "btnSzukaj")
        submit_button.click()

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'tabelaZbiorczaListaJednostek')))

        table = driver.find_element(By.CLASS_NAME, 'tabelaZbiorczaListaJednostek')
        rows = table.find_elements(By.CSS_SELECTOR, 'tr.tabelaZbiorczaListaJednostekAltRow')

        regon_link = rows[0].find_element(By.CSS_SELECTOR, 'a')
        regon_link.click()

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'tabelaRaportWewn')))

        self._get_legal_entity_details(driver)
        driver.quit()

    def _get_legal_entity_details(self, driver: webdriver) -> None:
        """
            Private method used to extract the legal entity details from the scraped page.

            :param driver: The webdriver object used to scrape the data.
            :return: None.
        """
        entity_type = self._identify_entity_type(driver)
        row_data = []

        if entity_type:
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

        self.data.loc[len(self.data)] = row_data

    def get_entity_info(self) -> pd.DataFrame:
        """
            Public method used to scrape the data from the database and return it as a pandas DataFrame.

            :param: None.
            :return: The scraped data as a pandas DataFrame.
        """
        with open(self.filepath, 'r') as f:
            for line in f:
                self._get_data(line.strip())

        return self.data
