import re
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
        self.col_names = []
        self.data = []

    def get_entity_info(self):
        with open(self.filepath, 'r') as f:
            for line in f:
                self._get_data(line.strip())

    def _identify_entity_type(self, driver: webdriver):
        if 'block' in driver.find_element(By.ID, 'tblRaportJFizyczna').get_attribute('style'):
            return 'fiz'
        elif 'block' in driver.find_element(By.ID, 'tblRaportJPrawna').get_attribute('style'):
            return 'praw'
        elif 'block' in driver.find_element(By.ID, 'tblRaportJLokalnaPrawnej').get_attribute('style'):
            print('tblRaportJLokalnaPrawnej')
        elif 'block' in driver.find_element(By.ID, 'tblRaportJLokalnaFizycznej').get_attribute('style'):
            print('tblRaportJLokalnaFizycznej')
        return 'th'

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

        general_data = [[cell.text for cell in row.find_elements(By.TAG_NAME, 'td')] for row in rows][0]

        # TODO
        # Wyciągnąć headery z tej samej tabeli (konkretnie Typ i Ulica, bo tylko te dane zabieramy)
        self.data.extend([general_data[1], general_data[8]])

        regon_link = rows[0].find_element(By.CSS_SELECTOR, 'a')
        regon_link.click()

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'tabelaRaportWewn')))

        self._get_legal_entity_details(driver)

        driver.quit()

    # TODO
    # Dorobić funkcje dla pozostałych typów (jednostka fizyczna, lokalna jednostka prawna, lokalna jednostka fizyczna)
    def _get_legal_entity_details(self, driver: webdriver):
        basic_table = driver.find_element(By.CLASS_NAME, 'tabelaRaportWewn')
        entity_type = self._identify_entity_type(driver)
        # REGON
        self.col_names.append(driver.find_element(By.ID, f'th{entity_type}_regon9').text)
        self.data.append(driver.find_element(By.ID, f'{entity_type}_regon9').text)
        # NIP
        self.col_names.append(driver.find_element(By.ID, f'th{entity_type}_nip').text)
        self.data.append(driver.find_element(By.ID, f'{entity_type}_nip').text)
        # NAZWA
        self.col_names.append('nazwa')
        self.data.append(driver.find_element(By.ID, f'{entity_type}_nazwa').text)
        # kod i nazwa podstawowej formy prawnej
        self.col_names.append('kod_i_nazwa_podstawowej_formy_prawnej')
        self.data.append(driver.find_element(By.ID, f'{entity_type}_nazwaPodstawowejFormyPrawnej').text)
        # kod i nazwa szczególnej formy prawnej
        self.col_names.append('kod_i_nazwa_szczegolnej_formy_prawnej')
        self.data.append(driver.find_element(By.ID, f'{entity_type}_nazwaSzczegolnejFormyPrawnej').text)
        # kod i nazwa formy własności
        self.col_names.append('kod_i_nazwa_formy_wlasnosci')
        self.data.append(driver.find_element(By.ID, f'{entity_type}_nazwaFormyWlasnosci').text)


        # kraj
        self.col_names.append('kraj')
        self.data.append(driver.find_element(By.ID, 'praw_adSiedzNazwaKraju').text)
        # województwo
        self.col_names.append('wojewodztwo')
        self.data.append(driver.find_element(By.ID, 'praw_adSiedzNazwaWojewodztwa').text)
        # powiat
        self.col_names.append('powiat')
        self.data.append(driver.find_element(By.ID, 'praw_adSiedzNazwaPowiatu').text)
        # gmina
        self.col_names.append('gmina')
        self.data.append(driver.find_element(By.ID, 'praw_adSiedzNazwaGminy').text)
        # miejscowość
        self.col_names.append('miejscowosc')
        self.data.append(driver.find_element(By.ID, 'praw_adSiedzNazwaMiejscowosci').text)
        # ulica
        self.col_names.append('ulica')
        self.data.append(driver.find_element(By.ID, 'praw_adSiedzNazwaUlicy').text)
        # nr nieruchomości
        self.col_names.append('nr_nieruchomosci')
        self.data.append(driver.find_element(By.ID, 'praw_adSiedzNumerNieruchomosci').text)
        # kod pocztowy
        self.col_names.append('kod_pocztowy')
        self.data.append(driver.find_element(By.ID, 'praw_adSiedzKodPocztowy').text)


        address_table = []
        # TODO
        # To samo powtórzyć dla tabeli z danymi adresowymi
        ...

        print(self.col_names)
        print(self.data)

    # TODO
    # Sklepać funkcyjke która to spakuje do jednego DF
    # Możesz od razu na DF działać zamiast na listach, to wtedy bez tego
