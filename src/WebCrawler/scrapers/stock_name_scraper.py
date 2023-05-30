"""
stock_name_scraper.py
====================================
This module is used to scrape entities stock name.
"""
import os
import time
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from typing import List
import logging
from WebCrawler.custom_logger import get_logger

class StockNameScraper:
    """
        Class responsible for scraping stock names for entities.

        Attributes:
            entities (pd.DataFrame): DataFrame containing entities data.
            print_info (bool): Flag indicating whether to print information during the scraping process.

    """

    def __init__(self, entities: pd.DataFrame, print_info=False):
        """
            Initializes an instance of StockNameScraper.

            :param entities: DataFrame containing entities data.
            :param print_info: Flag indicating whether to print information during the scraping process.
                Defaults to False.
            :return: None.
        """
        firefox_options = firefoxOptions()
        firefox_options.add_argument("--headless")
        service = Service(log_path=os.devnull)
        self.driver = webdriver.Firefox(options=firefox_options, service=service)
        self.driver.implicitly_wait(2)
        self.entities = entities
        self.print_info = print_info
        self.logger = get_logger()
        self.news_links = []
        self.stock_names = []

    def get_data(self) -> List[str]:
        """
            Public method used to retrieve the stock names for entities by calling private methods and returns a list of stock names.

            :param: None.
            :return: List of stock names for entities.
        """
        for count, entity in enumerate(self.entities.itertuples()):
            self.driver.delete_all_cookies()
            counter = str(count+1) + '/' + str(len(self.entities))
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

    def _get_entity_isin(self, entity_name: str, stock_type: str) -> str:
        """
            Private method used to retrieve the ISIN (International Securities Identification Number) of an entity
            based on its name and stock type.

            :param entity_name: Name of the entity for which the ISIN is to be retrieved.
            :param stock_type: Type of stock used for navigating to the corresponding stock exchange page.

            :return: ISIN of the entity if found, otherwise an empty string.
        """
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
            entity_link_element = ''
        if entity_link_element:
            return entity_link_element.get_attribute('href').split('=')[-1]
        return ''

    def _get_entity_stock_name(self, entity_isin: str) -> str:
        """
            Private method used to retrieve the stock name of an entity based on its ISIN (International Securities
            Identification Number).

            :param entity_isin: ISIN of the entity for which the stock name is to be retrieved.
            :return: Stock name of the entity if found, otherwise an empty string.
        """
        self.driver.get('https://infostrefa.com/infostrefa/pl/spolki')
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        td_elements = soup.find_all('td')

        for td in td_elements:
            if td.text.lower() == entity_isin.lower():
                return td.find('a')['href'].split(',')[-1]
        return ''
