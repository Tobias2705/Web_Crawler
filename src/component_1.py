import re
import pandas as pd
from typing import Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def check_nip_regon_krs(value: str) -> Union[str, None]:
    value = str(value)
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

    def get_entity_info(self):
        with open(self.filepath, 'r') as f:
            for line in f:
                self._get_data(line.strip())
            print(self.data)

    def _identify_entity_type(self, driver: webdriver):
        if 'block' in driver.find_element(By.ID, 'tblRaportJFizyczna').get_attribute('style'):
            return 'fiz'
        elif 'block' in driver.find_element(By.ID, 'tblRaportJPrawna').get_attribute('style'):
            return 'praw'
        elif 'block' in driver.find_element(By.ID, 'tblRaportJLokalnaPrawnej').get_attribute('style'):
            return 'lokpraw'
        elif 'block' in driver.find_element(By.ID, 'tblRaportJLokalnaFizycznej').get_attribute('style'):
            return 'lokfiz'
        return None

    def _get_data(self, key_value: str):
        url = "https://wyszukiwarkaregon.stat.gov.pl/appBIR/index.aspx"
        data_type = check_nip_regon_krs(key_value)
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        if data_type == 'NIP':
            input_data = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "txtNip")))
            submit_button = driver.find_element(By.ID, "btnSzukaj")
            input_data.send_keys(str(key_value))
            submit_button.click()
        elif data_type == 'REGON':
            input_data = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "txtRegon")))
            submit_button = driver.find_element(By.ID, "btnSzukaj")
            input_data.send_keys(str(key_value))
            submit_button.click()
        elif data_type == 'KRS':
            input_data = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "txtKrs")))
            submit_button = driver.find_element(By.ID, "btnSzukaj")
            input_data.send_keys(str(key_value))
            submit_button.click()

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'tabelaZbiorczaListaJednostek')))

        table = driver.find_element(By.CLASS_NAME, 'tabelaZbiorczaListaJednostek')
        rows = table.find_elements(By.CSS_SELECTOR, 'tr.tabelaZbiorczaListaJednostekAltRow')

        regon_link = rows[0].find_element(By.CSS_SELECTOR, 'a')
        regon_link.click()

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'tabelaRaportWewn')))

        self._get_legal_entity_details(driver)
        driver.quit()

    def _get_legal_entity_details(self, driver: webdriver):
        entity_type = self._identify_entity_type(driver)
        row_data = []
        if(entity_type):
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
