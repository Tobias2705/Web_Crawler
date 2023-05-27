import time
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
import logging
from WebCrawler.custom_logger import get_logger

class StockNameScraper:
    def __init__(self, entities: pd.DataFrame, print_info=False):
        firefox_options = firefoxOptions()
        firefox_options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.implicitly_wait(2)
        self.news_links = []
        self.entities = entities
        self.stock_names = []
        self.print_info = print_info
        self.logger = get_logger()

    def get_data(self):
        for count, entity in enumerate(self.entities.itertuples()):
            self.driver.delete_all_cookies()
            counter = f'{str(count + 1)}/{len(self.entities)}'
            try:
                entity_isin = self._get_entity_isin(entity.nazwa, 'newconnect')
                if not entity_isin:
                    entity_isin = self._get_entity_isin(entity.nazwa, 'gpw')
                entity_stock_name = self._get_entity_stock_name(entity_isin)
                self.stock_names.append(entity_stock_name)
                if self.print_info:
                    self.logger.info(f"{counter} StockNameScraper scraped: {entity.nip}")
            except:
                if self.print_info:
                    self.logger.error(f"{counter} StockNameScraper could not scrap: {entity.nip}")
                self.stock_names.append('')

        self.driver.quit()
        return self.stock_names

    def _get_entity_isin(self, entity_name: str, stock_type: str):
        entity_name = entity_name.replace('"', '')
        self.driver.get(f"https://www.{stock_type}.pl/spolki")
        search_input = self.driver.find_element(By.NAME, 'searchText')
        time.sleep(0.3)
        search_input.send_keys(entity_name)
        WebDriverWait(self.driver, 30).until(ec.invisibility_of_element_located((By.ID, 'preview-area')))
        time.sleep(0.8)
        try:
            entity_link_element = self.driver.find_element(By.XPATH, "//tbody[contains(@id, 'search-result')]/tr/td/a")
        except:
            entity_link_element = None
        if entity_link_element:
            return entity_link_element.get_attribute('href').split('=')[-1]
        return ''

    def _get_entity_stock_name(self, entity_isin: str):
        self.driver.get('https://infostrefa.com/infostrefa/pl/spolki')
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        td_elements = soup.find_all('td')

        for td in td_elements:
            if td.text.lower() == entity_isin.lower():
                return td.find('a')['href'].split(',')[-1]
