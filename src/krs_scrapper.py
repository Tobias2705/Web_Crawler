from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time

xpaths = {
    'NIP': "//ds-input[@label='Numer KRS']/*/input",
    'REGON': "//ds-input[@label='NIP']/*/input",
    'KRS': "//ds-input[@label='REGON']/*/input",
    'CheckboxP': "//ds-checkbox[@formcontrolname='rejestrP']/*/*/div[@class='p-checkbox-box']",
    'SearchButton': "//*[@id='p-panel-6-content']/div/div/div/ds-button[2]"
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

    def scrap(self):
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
        
KrsScrapper(5261184467, 'NIP').scrap()