import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


class InfoStrefaScrapper:
    def __init__(self, entities: str):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(30)
        self.news_links = []
        self.entities = entities
        self.news = pd.DataFrame(columns=[
            'spolka',
            'wiadomosc'
        ])

    def _get_news_links(self):
        self.news_links = []
        pages_num = self.driver.find_element(By.XPATH, "//ul[@class='pagination']/li[last()]").text

        for i in range(min(int(pages_num), 20)):
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            for td in soup.select('.search-results table.table.table-condensed.table-data td.text'):
                self.news_links.append(td.a['href'])

            next_page_btn = self.driver.find_element(By.XPATH, "//a[contains(@class, 'nav-next')]")
            if next_page_btn:
                next_page_btn.click()

    def get_data(self):
        self.driver.get('https://infostrefa.com/infostrefa/pl/index/')
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear()")
        self.driver.find_element(By.ID, 'rodoButtonAccept').click()
        for entity in self.entities:
            entity_name = entity.replace("SPÓŁKA AKCYJNA", "SA").replace("ALTERNATYWNA SPÓŁKA INWESTYCYJNA", "ASI")
            entity_id = self._get_entity_id(entity_name)
            if entity_id:
                self.driver.get(
                    f"https://infostrefa.com/infostrefa/pl/wiadomosci/szukaj/1?company={entity_id}&category=wszystko")
            else:
                continue
            self._get_news_links()
            self._get_news(entity_name)
        print(self.news)

    def _get_entity_id(self, entity):
        self.driver.get("https://infostrefa.com/infostrefa/pl/spolki")
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        td_elements = soup.find_all('td')

        for td in td_elements:
            if td.text.lower() == entity.lower():
                id = td.find('a')['href'].split('/')[-1].split(',')[0]
                return id

    def _get_news(self, entity_name: str):
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
                            if index != len(tds) - 1:
                                text += ';'
                            else:
                                text += '\n'
            print([entity_name, text])
            self.news.loc[len(self.news)] = [entity_name, text]


scrapper = InfoStrefaScrapper(['CD PROJEKT SPÓŁKA AKCYJNA', 'ZE PAK SPÓŁKA AKCYJNA'])
scrapper.get_data()