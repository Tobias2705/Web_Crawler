import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def check_nip_regon_krs(value):
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


def get_data(key_value):
    url = "https://wyszukiwarkaregon.stat.gov.pl/appBIR/index.aspx"
    data_type = check_nip_regon_krs(key_value)
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    if data_type == 'NIP':
        input_data = soup.find("input", {"id": "txtNip"})
        input_data["value"] = str(key_value)
    elif data_type == 'REGON':
        input_data = soup.find("input", {"id": "txtRegon"})
        input_data["value"] = str(key_value)
    elif data_type == 'KRS':
        input_data = soup.find("input", {"id": "txtKrs"})
        input_data["value"] = str(key_value)

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
    results = [[cell.text for cell in row.find_elements(By.TAG_NAME, 'td')] for row in rows]
    driver.quit()

    return pd.DataFrame(results)


class RegonDatabaseScrapper:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_entity_info(self):
        df = pd.DataFrame()

        with open(self.filepath, 'r') as f:
            for line in f:
                df = pd.concat([df, get_data(line.strip())], ignore_index=True)
            df.columns = ['Regon', 'Typ', 'Nazwa', 'Województwo', 'Powiat', 'Gmina', 'Kod pocztowy',
                                   'Miejscowość', 'Ulica', 'Informacja o skreśleniu z REGON']
            print(df[['Regon', 'Typ', 'Nazwa']])
