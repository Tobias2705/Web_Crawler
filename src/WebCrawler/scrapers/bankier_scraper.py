"""
bankier_scraper.py
====================================
This module is used to scrape data from bankier.pl website.
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
from WebCrawler.custom_logger import get_logger


class BankierScraper:
    """
        Class responsible for scraping data from bankier.pl website.

        Attributes:
            entities: DataFrame containing entities data.
            print_info: Flag indicating whether to print information during the scraping process.
    """
    def __init__(self, entities: pd.DataFrame, print_info=False):
        """
            Initializes an instance of BankierScraper.

            :param entities: DataFrame containing entities data.
            :param print_info: Flag indicating whether to print information during the scraping process.
                Defaults to False.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(30)
        self.forum_link = ''
        self.messages_link = ''
        self.news_link = ''
        self.entities = entities
        self.news = pd.DataFrame(columns=[
            'nip',
            'data',
            'wiadomosc'
        ])
        self.print_info = print_info
        self.logger = get_logger()

    def get_data(self) -> pd.DataFrame:
        """
            Public method used to scrape data from bankier.pl for each entity and returns a DataFrame.

            :param: None.
            :return: DataFrame containing scraped data.

        """
        for count, entity in enumerate(self.entities.itertuples()):
            counter = str(count+1) + '/' + str(len(self.entities))
            try:
                self.driver.get(
                    f"https://www.bankier.pl/inwestowanie/profile/quote.html?symbol={entity.nazwa_gieldowa}")
                self.forum_link = self.driver.find_element(By.XPATH, "//div[contains(@id, 'boxForum')]/div[contains("
                                                                     "@class, 'boxFooter')]/a").get_attribute('href')
                self.messages_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Więcej komunikatów')]").get_attribute('href')
                self.news_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Więcej wiadomości')]").get_attribute('href')
                self._get_forum(entity.nip)
                self._get_messages(entity.nip)
                self._get_news(entity.nip)
                if self.print_info:
                    self.logger.info(f"{counter} BankierScraper scraped: {entity.nip}")
            except:
                if self.print_info:
                    self.logger.error(f"{counter} BankierScraper could not scrap: {entity.nip}")

        self.driver.quit()
        return self.news

    def _get_news(self, entity: str) -> None:
        """
            Private method used to scrape news for a given entity.

            :param entity: Entity identifier.
            :return: None.
        """
        news_links = []
        self.driver.get(self.news_link)
        for i in range(1):
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            news_elements = soup.find('section', {'id': 'articleList'}).find_all('a', {'class': 'more-link'})
            for news_element in news_elements:
                news_links.append(news_element.get('href'))
        for link in news_links:
            self.driver.get(f"https://bankier.pl{link}")
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            article_attributes = soup.find('div', {'class': 'm-article-attributes'}).find_all('div')
            date = ''
            for attribute in article_attributes:
                if "publikacja" in attribute.text:
                    date = attribute.find('span').text
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M").strftime("%H:%M %d/%m/%Y")
            news_section = soup.find('section', {'class': 'o-article-content'})
            paragraphs = news_section.find_all('p')
            news = ''
            for paragraph in paragraphs:
                news += paragraph.text
            self.news.loc[len(self.news)] = [entity, date, news]

    def _get_messages(self, entity: str) -> None:
        """
            Private method used to scrape messages for a given entity.

            :param entity: Entity identifier.
            :return: None.
        """
        messages_links = []
        self.driver.get(self.messages_link)
        for i in range(1):
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            articles_div = soup.find('section', {'id': 'articleEspiList'})
            div_elements = articles_div.find_all('div', {'class': 'article'})
            for div in div_elements:
                link_element = div.find('a')
                if link_element:
                    href = link_element.get('href')
                    messages_links.append(href)
            next_page_element = articles_div.find('a', {'class': 'next'})
            if next_page_element:
                self.driver.get(f"https://bankier.pl{next_page_element.get('href')}")
            else:
                break

        for link in messages_links:
            self.driver.get(f"https://bankier.pl{link}")
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            date = soup.find('div', {'class': 'm-article-attributes'}).find_all('div')[0].text
            date = datetime.strptime(date, "%Y-%m-%d %H:%M").strftime("%H:%M %d/%m/%Y")
            td_elements = soup.find_all('td', {'colspan': True})
            tr_element = None
            for td in td_elements:
                if td.text.strip() == 'Treść raportu:':
                    tr_element = td.parent
                    break
            if tr_element:
                next_tr = tr_element.find_next_sibling('tr')
                if next_tr:
                    td_content = next_tr.find('td', {'colspan': True}).text
                    self.news.loc[len(self.news)] = [entity, date, td_content]

    def _get_forum(self, entity: str) -> None:
        """
            Private method used to scrape forum data for a given entity.

            :param entity: Entity identifier.
            :return: None.
        """
        thread_links = []
        self.driver.get(self.forum_link)
        for i in range(1):
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            tr_elements = soup.find('table', {'class': 'threadsList'}).find_all('tr')
            for tr_element in tr_elements:
                thread_links.append(tr_element.find('a').get('href'))
            next_btn = soup.find('div', {'class': 'pagination'}).find('a', {'class': 'next'})
            if next_btn:
                self.driver.get(f"https://bankier.pl{next_btn.get('href')}")
            else:
                break
        for link in thread_links:
            self.driver.get(f"https://bankier.pl/forum/{link}")
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            date = soup.find('div', {'class': 'entry-meta'}).find('time', {'class': 'entry-date'}).text.strip()
            date = datetime.strptime(date, "%Y-%m-%d %H:%M").strftime("%H:%M %d/%m/%Y")
            show_all = soup.find('a', {'id': 'showAllThread'})
            text = ''
            if show_all:
                self.driver.get(f"https://bankier.pl/forum/{show_all.get('href')}")
                while True:
                    html = self.driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    thread_tree = soup.find('ul', {'class': 'threadTree'})
                    if thread_tree:
                        li_elements = thread_tree.find_all('li')
                        for li_element in li_elements:
                            text += li_element.find('div', {'class': 'p'}).text
                    next_btn = soup.find('div', {'class': 'pagination'}).find('a', {'class': 'next'})
                    if next_btn:
                        self.driver.get(f"https://bankier.pl{next_btn.get('href')}")
                    else:
                        break
            else:
                text = soup.find('div', {'id': 'boxThread'}).find('div', {'class': 'p'}).text
            self.news.loc[len(self.news)] = [entity, date, text]
