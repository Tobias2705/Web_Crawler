import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import logging
from WebCrawler.custom_logger import get_logger


class InfoStrefaScrapper:
    def __init__(self, entities: pd.DataFrame, print_info = False):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(30)
        self.news_links = []
        self.entities = entities
        self.news = pd.DataFrame(columns=[
            'nip',
            'data',
            'wiadomosc'
        ])
        self.print_info = print_info
        self.logger = get_logger()

    def _get_news_links(self):
        self.news_links = []
        pages_num = self.driver.find_element(By.XPATH, "//ul[@class='pagination']/li[last()]").text

        for _ in range(min(int(pages_num), 1)):
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            self.news_links.extend(td.a['href'] for td in soup.select('.search-results table.table.table-condensed.table-data td.text'))

            if next_page_btn := self.driver.find_element(By.XPATH, "//a[contains(@class, 'nav-next')]"):
                next_page_btn.click()

    def get_data(self):
        self.driver.get('https://infostrefa.com/infostrefa/pl/index/')
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear()")
        self.driver.find_element(By.ID, 'rodoButtonAccept').click()
        for count, entity in enumerate(self.entities.itertuples()):
            counter = f'{str(count + 1)}/{len(self.entities)}'
            try:
                if entity_id := self._get_entity_id(entity.nazwa_gieldowa):
                    self.driver.get(
                        f"https://infostrefa.com/infostrefa/pl/wiadomosci/szukaj/1?company={entity_id}&category=wszystko")
                else:
                    continue
                self._get_news_links()
                self._get_news(entity.nip)
                if self.print_info:
                    self.logger.info(f"{counter} InfostrefaScraper scraped: {entity.nip}")
            except:
                if self.print_info:
                    self.logger.error(f"{counter} InfostrefaScraper could not scrap: {entity.nip}")

        self.driver.quit()
        return self.news

    def _get_entity_id(self, entity: str):
        self.driver.get("https://infostrefa.com/infostrefa/pl/spolki")
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        td_elements = soup.find_all('td')

        for td in td_elements:
            if td.text.lower() == entity.lower():
                return td.find('a')['href'].split('/')[-1].split(',')[0]

    def _get_news(self, entity: str):
        for i in range(len(self.news_links)):
            self.driver.get(f"https://infostrefa.com{self.news_links[i]}")
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            divs = soup.find_all('div', {'class': 'news-full-content'})
            text = ""
            for div in divs:
                p = div.find('p')
                if p is not None:
                    text += p.text + '\n'
                else:
                    trs = div.find_all('tr')
                    for tr in trs:
                        tds = tr.find_all('td')
                        for index, td in enumerate(tds):
                            text += td.text
                            text += ';' if index != len(tds) - 1 else '\n'
            date = soup.find('div', {'class': 'text-date'}).text
            self.news.loc[len(self.news)] = [entity, date, text]
