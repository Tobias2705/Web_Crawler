from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd

xpaths = {
    'KRS': "//ds-input[@label='Numer KRS']/*/input",
    'NIP': "//ds-input[@label='NIP']/*/input",
    'REGON': "//ds-input[@label='REGON']/*/input",
    'CheckboxP': "//ds-checkbox[@formcontrolname='rejestrP']/*/*/div[@class='p-checkbox-box']",
    'SearchButton': "//*[@id='p-panel-6-content']/div/div/div/ds-button[2]",
    'Table': "//*[@id='p-panel-5-content']/div/div/ds-table/div/p-table/div/div/table",
    'Link': "//*[@class='link']",
    'ReprSection': "//ds-panel[@id='sekcja10']"
}

class KrsScrapper:
    def __init__(self, id, id_type):
        self.url = 'https://wyszukiwarka-krs.ms.gov.pl/'
        self._set_driver()
        self.id = id
        self.id_type = id_type

    def _set_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()

    def scrap(self):
        representants = pd.DataFrame(columns=[
            'nazwisko',
            'nazwisko_drugi_czlon',
            'imie_pierwsze',
            'imie_drugie',
            'funkcja'
        ])

        self.driver.get(self.url)

        # search and input id
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, xpaths[self.id_type])))
        input_element = self.driver.find_element(By.XPATH, xpaths[self.id_type])
        input_element.send_keys(self.id)

        # mark 'Przedsiębiorcy' checkbox
        checkbox_element = self.driver.find_element(By.XPATH, xpaths['CheckboxP'])
        checkbox_element.click()

        # click search button
        search_button_element = self.driver.find_element(By.XPATH, xpaths['SearchButton'])
        search_button_element.click()

        # search table's first row
        table_element = self.driver.find_element(By.XPATH, xpaths['Table'])

        first_link_element = None
        try:
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, xpaths['Link'])))
        except:
            print(f"Not found {self.id_type}: {self.id} in KRS.")
            return

        # first_link_element.click() # ERROR not clickable ?? couldn't click because it's overlapping with footer?
        self.driver.execute_script("document.getElementsByClassName('link')[0].click()")

        # search section with representants
        WebDriverWait(self.driver, 30).until(ec.presence_of_element_located((By.XPATH, xpaths['ReprSection'])))
        repr_section = self.driver.find_element(By.XPATH, xpaths['ReprSection'])

        # search representants in rows
        rows = repr_section.find_elements(By.XPATH, '//tbody/tr')
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, 'td')
            row_data = []
            for column in columns:
                value = column.find_element(By.CLASS_NAME, 'ds-column-value').text
                row_data.append(value)
            representants.loc[len(representants)] = row_data

        return representants

        
# scraper = KrsScrapper(5261184467, 'NIP')
# print(scraper.scrap())