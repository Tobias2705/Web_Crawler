from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from component_1 import check_nip_regon_krs
import time

class KrsScrapper:
    search_input_xpath = {
        'NIP':   '/html/body/app-root/ds-layout/div/div/div/main/ds-layout-content/app-wyszukiwarka-krs/div/div[3]/ds-tab-view/div/div[1]/app-wyszukaj-podmiot/div/div[1]/ds-panel[1]/p-panel/div/div[2]/div/div/ds-panel[2]/p-panel/div/div[2]/div/div/div/div[1]/div[2]/ds-input/div[1]/input',
        'REGON': '/html/body/app-root/ds-layout/div/div/div/main/ds-layout-content/app-wyszukiwarka-krs/div/div[3]/ds-tab-view/div/div[1]/app-wyszukaj-podmiot/div/div[1]/ds-panel[1]/p-panel/div/div[2]/div/div/ds-panel[2]/p-panel/div/div[2]/div/div/div/div[1]/div[3]/ds-input/div[1]/input',
        'KRS':   '/html/body/app-root/ds-layout/div/div/div/main/ds-layout-content/app-wyszukiwarka-krs/div/div[3]/ds-tab-view/div/div[1]/app-wyszukaj-podmiot/div/div[1]/ds-panel[1]/p-panel/div/div[2]/div/div/ds-panel[2]/p-panel/div/div[2]/div/div/div/div[1]/div[1]/ds-input/div[1]/input'
    }
    checkbox_xpath = '/html/body/app-root/ds-layout/div/div/div/main/ds-layout-content/app-wyszukiwarka-krs/div/div[3]/ds-tab-view/div/div[1]/app-wyszukaj-podmiot/div/div[1]/ds-panel[1]/p-panel/div/div[2]/div/div/ds-panel[1]/p-panel/div/div[2]/div/div/div/ds-checkbox[1]/p-checkbox/div/div[2]'
    search_button_xpath = '//*[@id="p-panel-6-content"]/div/div/div/ds-button[2]/p-button/button/span'

    def __init__(self, id):
        self.url = 'https://wyszukiwarka-krs.ms.gov.pl/'
        self._set_driver()
        self.id = id
        self.id_type = check_nip_regon_krs(id)

    def _set_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrap(self):
        self.driver.get(self.url)

        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, self.search_input_xpath[self.id_type])))
        input_text_element = self.driver.find_element(By.XPATH, self.search_input_xpath[self.id_type])
        input_text_element.send_keys(self.id)

        checkbox_element = self.driver.find_element(By.XPATH, self.checkbox_xpath)
        checkbox_element.click()

        search_button_element = self.driver.find_element(By.XPATH, self.search_button_xpath)
        search_button_element.click()

        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'p-datatable-tbody')))
        table_element = self.driver.find_element(By.CLASS_NAME, 'p-datatable-tbody')

        link_element = table_element.find_element(By.CLASS_NAME, 'link')
        print(link_element)
        link_element.click()

        print("yay")

        

nip = '5261184467'
scrapper = KrsScrapper(nip)

print(scrapper.id_type, scrapper.id, '\n')

print('scrapping:')
scrapper.scrap()