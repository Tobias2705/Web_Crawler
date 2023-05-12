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
    'RegonInfo': '//*[@id="p-panel-16-content"]/div/div/div/div[10]',
    'NIPInfo': '//*[@id="p-panel-16-content"]/div/div/div/div[8]',
    'KRSInfo': '//*[@id="p-panel-16-content"]/div/div/div/div[6]',
    'NameInfo': '//*[@id="p-panel-16-content"]/div/div/div/div[2]',
    'WWWSite': '//*[@id="p-panel-21-content"]/div/div/div/div[2]', 
    'Email': '//*[@id="p-panel-21-content"]/div/div/div/div[4]',
    'NameOfRepr': '//*[@id="p-panel-24-content"]/div/div/div/div[2]',
    'WayOfRepr': '//*[@id="p-panel-24-content"]/div/div/div/div[4]',
    'NextPage': "//*[@class='p-paginator-next p-paginator-element p-link p-ripple']"
}

class KrsScrapper:
    def __init__(self, id, id_type, headless = True):
        self.url = 'https://wyszukiwarka-krs.ms.gov.pl/'
        self.id = id
        self.id_type = id_type
        self.headless = headless

    def scrap(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=chrome_options)
        driver.fullscreen_window()
        driver.get(self.url)

        # search and input id
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, xpaths[self.id_type])))
        input_element = driver.find_element(By.XPATH, xpaths[self.id_type])
        input_element.send_keys(self.id)

        # mark 'Przedsiębiorcy' checkbox        
        checkbox_element = driver.find_element(By.XPATH, xpaths['CheckboxP'])
        checkbox_element.click()

        # click search button
        search_button_element = driver.find_element(By.XPATH, xpaths['SearchButton'])
        search_button_element.click()

        # search table's first row
        table_element = driver.find_element(By.XPATH, xpaths['Table'])

        first_link_element = None
        try:
            WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, xpaths['Link'])))
        except:
            raise(f"KrsScrapper: Not found {self.id_type}: {self.id} in KRS.")

        driver.execute_script("document.getElementsByClassName('link')[0].click()")

        # search Forma prawna
        WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, xpaths['LegalForm'])))
        legal_form_element = driver.find_element(By.XPATH, xpaths['LegalForm'])
        legal_form = legal_form_element.text

        # search namme
        name_info_element = driver.find_element(By.XPATH, xpaths['NameInfo'])
        name_info = name_info_element.text

        # search KRS
        krs_info_element = driver.find_element(By.XPATH, xpaths['KRSInfo'])
        krs_info = krs_info_element.text

        # search NIP
        nip_info_element = driver.find_element(By.XPATH, xpaths['NIPInfo'])
        nip_info = nip_info_element.text

        # search REGON
        regon_info_element = driver.find_element(By.XPATH, xpaths['RegonInfo'])
        regon_info = regon_info_element.text

        # search Data wpisu do Rejestru Przedsiębiorców
        date_entry_element = driver.find_element(By.XPATH, xpaths['DataEntry'])
        date_entry = date_entry_element.text

        # search Data wykreślenia z Rejestru Przedsiębiorców
        date_removal_element = driver.find_element(By.XPATH, xpaths['DataDeletion'])
        date_removal = date_removal_element.text

        # search Adres WWW
        www_address_element = driver.find_element(By.XPATH, xpaths['WWWSite'])
        www_address = www_address_element.text

        # seach E-mail
        email_element = driver.find_element(By.XPATH, xpaths['Email'])
        email = email_element.text

        # search Nazwa organu reprezentacji
        nameofrepr_element = driver.find_element(By.XPATH, xpaths['NameOfRepr'])
        nameofrepr = nameofrepr_element.text

        # search Sposób reprezentacji
        wayofrepr_element = driver.find_element(By.XPATH, xpaths['WayOfRepr'])
        wayofrepr = wayofrepr_element.text

        # search section with representants
        WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, xpaths['ReprSection'])))
        repr_section = driver.find_element(By.XPATH, xpaths['ReprSection'])

        representants = pd.DataFrame(columns=[
            'nip',
            'imie',
            'imie2',
            'nazwisko',
            'nazwisko2',
            'funkcja'
        ])

        # search Członkowie reprezentacji in rows
        while True:
            WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, '//tbody/tr')))
            rows = repr_section.find_elements(By.XPATH, '//tbody/tr')
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
                row_data = [nip_info]
                for column in columns:
                    value = column.find_element(By.CLASS_NAME, 'ds-column-value').text
                    row_data.append(value)
                row_data_ordered = [row_data[0], row_data[3], row_data[4], row_data[1], row_data[2], row_data[5]]
                representants.loc[len(representants)] = row_data_ordered

            try:
                next_page_element = driver.find_element(By.XPATH, xpaths['NextPage'])
                driver.execute_script("document.getElementsByClassName('p-paginator-next p-paginator-element p-link p-ripple')[0].click()")
            except:
                break

        general_info = {
            "nazwa": name_info,
            "krs": krs_info,
            "nip": nip_info,
            "regon": regon_info,
            "forma_prawna": legal_form,
            "data_wpisu_do_rej_przeds": date_entry,
            "data_wykr_z_rej_przeds": date_removal,
            "nazwa_org_repr": nameofrepr,
            "sposob_repr": wayofrepr,
            "adr_www": www_address,
            "email": email,
        }

        return general_info, representants
