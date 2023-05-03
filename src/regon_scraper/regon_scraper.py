"""
regon_scraper.py
====================================
This module is used to scrape information from the REGON database.
"""

import time
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from typing import Union, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


class RegonScraper:
    """
    This class is used to create a scraper that scrapes information about entities from the REGON database.
    It is initialised with the following parameters.

    Attributes:
        entity_data (pandas.DataFrame): The DataFrame where the scraped data about entities will be stored.
        local_entity_data (pandas.DataFrame): The DataFrame where the scraped data about local entities will be stored.
        key_type (dict): The dictionary containing the keys and their corresponding identifiers used for crawling.
        entity_type (dict): The dictionary containing the entity types and their corresponding identifiers used
                            for scarping.
        local_entity_type (dict): The dictionary containing the local entity types and their corresponding identifiers
                            used for scarping.
    """

    def __init__(self):
        """
        Initializes the RegonScraper class.
        """
        self.local_regons = []
        self.rows = 0
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(30)
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
        self.pkd = pd.DataFrame(columns=[
            'regon',
            'kod',
            'nazwa'
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
        entity_type = next((entity_type for entity_id, entity_type in self.entity_type.items() if
                            'block' in driver.find_element(By.ID, entity_id).get_attribute('style')), None)
        return entity_type

    def _identify_local_entity_type(self, driver: webdriver) -> Union[str, None]:
        """
            Private method used to identify the type of the local entity in the database.

            :param driver: The webdriver object used to scrape the data.
            :return: The local entity type identifier as a string.
        """
        l_entity_type = next((l_entity_type for l_entity_id, l_entity_type in self.local_entity_type.items() if
                              'table' in driver.find_element(By.ID, l_entity_id).get_attribute('style')), None)
        return l_entity_type

    def _get_data(self, key_value: str, idx: int, data_type: str):
        """
            Private method used to scrape the data from the database.

            :param key_value: The key value used to search for the entity in the database.
            :param idx: Value specifying the number of the line to be analysed.
            :return: None.
        """
        self.driver.get("https://wyszukiwarkaregon.stat.gov.pl/appBIR/index.aspx")
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear()")

        input_data = WebDriverWait(self.driver, 30).until(ec.element_to_be_clickable((By.ID, self.key_type[data_type])))
        time.sleep(0.5)
        input_data.send_keys(str(key_value))

        submit_button = self.driver.find_element(By.ID, "btnSzukaj")
        submit_button.click()
        time.sleep(0.5)

        table_body = self.driver.find_element(By.CLASS_NAME, 'tabelaZbiorczaListaJednostek').find_element(By.TAG_NAME,
                                                                                                          'tbody')
        rows = table_body.find_elements(By.TAG_NAME, 'tr')
        self.rows = len(rows)

        regon_link = rows[idx].find_element(By.TAG_NAME, 'a')
        regon_link.click()
        time.sleep(0.5)

        entity_type = self._identify_entity_type(self.driver)

        self._get_entity_details(self.driver, entity_type)
        self._check_if_local_entities_exist(self.driver, entity_type)

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

            self._get_pkd(self.driver, entity_type, row_data[0])
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

        self._get_pkd(self.driver, entity_type, row_data[0])
        self.local_entity_data.loc[len(self.local_entity_data)] = row_data

    def _check_if_local_entities_exist(self, driver: webdriver, entity_type):
        """
            Private method used to check if local entities exist.

            :param driver: The webdriver object used to scrape the data.
            :param entity_type: The local entity type identifier as a string.
            :return: None.
        """
        self.local_regons = []
        if entity_type in ['fiz', 'praw']:
            if 'table' in driver.find_element(By.ID, f'{entity_type}_lokTable').get_attribute('style'):
                list_button = driver.find_element(By.ID, f'{entity_type}_butLinkLok')
                list_button.click()
                time.sleep(0.5)
                td = driver.find_element(By.ID, f'{entity_type}_lok')
                body = td.find_element(By.TAG_NAME, 'tbody')
                rows = body.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    self.local_regons.append(row.find_element(By.TAG_NAME, 'a').text)

    def _get_pkd(self, driver: webdriver, entity_type, regon) -> None:
        """
            Private method used to extract pkd information.

            :param driver: The webdriver object used to scrape the data.
            :param entity_type: The local entity type identifier as a string.
            :param regon: REGON of the entity for which we are extracting pkd
            :return: None.
        """
        driver.find_element(By.ID, f'{entity_type}_butLinkDzial').click()
        time.sleep(0.5)
        td = driver.find_element(By.ID, f'{entity_type}_dzial')
        tables = td.find_elements(By.TAG_NAME, 'table')
        for table in tables:
            body = table.find_element(By.TAG_NAME, 'tbody')
            self.driver.implicitly_wait(.1)
            rows = body.find_elements(By.TAG_NAME, 'tr')
            self.driver.implicitly_wait(30)
            for row in rows:
                data = row.find_elements(By.TAG_NAME, 'td')
                self.pkd.loc[len(self.pkd)] = [regon, data[0].text, data[1].text]

    def get_entity_info(self, number: str, num_type: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Public method used to scrape the data from the database and return it as a pandas DataFrame.

        :param: None.
        :return: The scraped data as a pandas DataFrame.
        """
        self.reset_dataframes()
        self._get_data(number, 0, num_type)
        for regon in self.local_regons:
            self._get_data(regon.strip(), 0, 'REGON')
        for idx in range(1, self.rows):
            self._get_data(number, idx, num_type)
            for regon in self.local_regons:
                self._get_data(regon.strip(), 0, 'REGON')
        return self.entity_data, self.local_entity_data, self.pkd

    def reset_dataframes(self):
        self.entity_data.drop(self.entity_data.index,inplace=True)
        self.local_entity_data.drop(self.local_entity_data.index,inplace=True)
        self.pkd.drop(self.pkd.index,inplace=True)
