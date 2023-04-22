from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import pprint

xpaths = {
    'KRS': "//ds-input[@label='Numer KRS']/*/input",
    'NIP': "//ds-input[@label='NIP']/*/input",
    'REGON': "//ds-input[@label='REGON']/*/input",
    'CheckboxP': "//ds-checkbox[@formcontrolname='rejestrP']/*/*/div[@class='p-checkbox-box']",
    'SearchButton': "//*[@id='p-panel-6-content']/div/div/div/ds-button[2]",
    'Table': "//*[@id='p-panel-5-content']/div/div/ds-table/div/p-table/div/div/table",
    'Link': "//*[@class='link']",
    'ReprSection': "//ds-panel[@id='sekcja10']",
    'DataEntry': '//*[@id="p-panel-17-content"]/div/div/div/div[2]',
    'DataDeletion': '//*[@id="p-panel-17-content"]/div/div/div/div[4]',
    'LegalForm': '//*[@id="p-panel-16-content"]/div/div/div/div[12]',
    'WWWSite': '//*[@id="p-panel-21-content"]/div/div/div/div[2]', 
    'Email': '//*[@id="p-panel-21-content"]/div/div/div/div[4]',
    'NameOfRepr': '//*[@id="p-panel-24-content"]/div/div/div/div[2]',
    'WayOfRepr': '//*[@id="p-panel-24-content"]/div/div/div/div[4]',
    'NextPage': "//*[@class='p-paginator-next p-paginator-element p-link p-ripple']"
}

class KrsScrapper:
    def __init__(self, id, id_type, headless = True):
        self.url = 'https://wyszukiwarka-krs.ms.gov.pl/'
        self.headless = headless
        self._set_driver()
        self.id = id
        self.id_type = id_type

    def _set_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.fullscreen_window()

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

        # search table's first row
        table_element = self.driver.find_element(By.XPATH, xpaths['Table'])

        first_link_element = None
        try:
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, xpaths['Link'])))
        except:
            print(f"Not found {self.id_type}: {self.id} in KRS.")
            return

        self.driver.execute_script("document.getElementsByClassName('link')[0].click()")

        # search Forma prawna
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, xpaths['LegalForm'])))
        legal_form_element = self.driver.find_element(By.XPATH, xpaths['LegalForm'])
        legal_form = legal_form_element.text

        # search Data wpisu do Rejestru Przedsiębiorców
        date_entry_element = self.driver.find_element(By.XPATH, xpaths['DataEntry'])
        date_entry = date_entry_element.text

        # search Data wykreślenia z Rejestru Przedsiębiorców
        date_removal_element = self.driver.find_element(By.XPATH, xpaths['DataDeletion'])
        date_removal = date_removal_element.text

        # search Adres WWW
        www_address_element = self.driver.find_element(By.XPATH, xpaths['WWWSite'])
        www_address = www_address_element.text

        # seach E-mail
        email_element = self.driver.find_element(By.XPATH, xpaths['Email'])
        email = email_element.text

        # search Nazwa organu reprezentacji
        nameofrepr_element = self.driver.find_element(By.XPATH, xpaths['NameOfRepr'])
        nameofrepr = nameofrepr_element.text

        # search Sposób reprezentacji
        wayofrepr_element = self.driver.find_element(By.XPATH, xpaths['WayOfRepr'])
        wayofrepr = wayofrepr_element.text

        # search section with representants
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, xpaths['ReprSection'])))
        repr_section = self.driver.find_element(By.XPATH, xpaths['ReprSection'])

        representants = pd.DataFrame(columns=[
            'nazwisko',
            'nazwisko_drugi_czlon',
            'imie_pierwsze',
            'imie_drugie',
            'funkcja'
        ])

        # search Członkowie reprezentacji in rows
        while True:
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, '//tbody/tr')))
            rows = repr_section.find_elements(By.XPATH, '//tbody/tr')
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
                row_data = []
                for column in columns:
                    value = column.find_element(By.CLASS_NAME, 'ds-column-value').text
                    row_data.append(value)
                representants.loc[len(representants)] = row_data

            try:
                next_page_element = self.driver.find_element(By.XPATH, xpaths['NextPage'])
                self.driver.execute_script("document.getElementsByClassName('p-paginator-next p-paginator-element p-link p-ripple')[0].click()")
            except:
                break

        result = {
            "Forma prawna": legal_form,
            "Data wpisu do Rejestru Przedsiębiorców": date_entry,
            "Data wykreślenia z Rejestru Przedsiębiorców": date_removal,
            "Nazwa organu reprezentacji": nameofrepr,
            "Sposób reprezentacji": wayofrepr,
            "Adres WWW": www_address,
            "E-mail": email,
            "Członkowie reprezentacji": representants.to_dict('records')
        }

        return result
