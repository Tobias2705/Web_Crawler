import time
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup


class InfoStrefaScrapper:
    def __init__(self, entities: pd.DataFrame, print_info = False):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        firefox_options = firefoxOptions()
        firefox_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.firefoxDriver = webdriver.Firefox(options=firefox_options)
        self.driver.implicitly_wait(30)
        self.news_links = []
        self.entities = entities
        self.news = pd.DataFrame(columns=[
            'spolka',
            'data',
            'wiadomosc'
        ])
        self.print_info = print_info

    def _get_news_links(self):
        self.news_links = []
        pages_num = self.driver.find_element(By.XPATH, "//ul[@class='pagination']/li[last()]").text

        for i in range(min(int(pages_num), 1)):
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
        for count, entity in enumerate(self.entities.itertuples()):
            counter = str(count+1) + '/' + str(len(self.entities))
            try:
                entity_isin = self._get_entity_isin(entity.nazwa)
                entity_id = self._get_entity_id(entity_isin)
                if entity_id:
                    self.driver.get(
                        f"https://infostrefa.com/infostrefa/pl/wiadomosci/szukaj/1?company={entity_id}&category=wszystko")
                else:
                    continue
                self._get_news_links()
                self._get_news(entity.nip)
                if self.print_info:
                    print(f"{counter} InfostrefaScraper scraped: {entity.nip}")
            except:
                if self.print_info:
                    print(f"{counter} InfostrefaScraper could not scrap: {entity.nip}")

        self.driver.quit()
        self.firefoxDriver.quit()
        return self.news

    def _get_entity_id(self, entity: str):
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
            date = soup.find('div', {'class': 'text-date'}).text
            self.news.loc[len(self.news)] = [entity_name, date, text]

    def _get_entity_isin(self, entity_name: str):
        entity_name = entity_name.replace('"', '')
        self.firefoxDriver.get("https://www.gpw.pl/spolki")
        search_input = self.firefoxDriver.find_element(By.NAME, 'searchText')
        time.sleep(0.5)
        search_input.send_keys(entity_name)
        WebDriverWait(self.firefoxDriver, 60).until(ec.invisibility_of_element_located((By.ID, 'preview-area')))
        entity_link = self.firefoxDriver.find_element(By.XPATH, "//tbody[contains(@id, 'search-result')]/tr/td/a").get_attribute('href')
        return entity_link.split('=')[-1]
