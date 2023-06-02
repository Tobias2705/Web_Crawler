import requests
from bs4 import BeautifulSoup
import time


def get_href_links(tax_identifier, print_info=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'}
    url = f"https://aleo.com/int/companies?phrase='{tax_identifier}'"
    for i in range(10):
        response = requests.get(url, headers=headers)
        time.sleep(1)

    soup = BeautifulSoup(response.content, "html.parser")
    href_links = []
    for div in soup.find_all("div", {"class": "catalog-row-first-line"}):
        for a in div.find_all("a", {"class": "catalog-row-first-line__company-name"}):
            href_links.append(a.get("href"))
    if print_info:
        print(href_links[0])
    url = f"https://aleo.com/int/{href_links[0]}"
    if print_info:
        print(url)
    for i in range(10):
        response = requests.get(url, headers=headers)
        time.sleep(1)
    soup = BeautifulSoup(response.content, "html.parser")

    account_numbers = []
    for account in soup.find_all('div', {'class': 'bank-account__number'}):
        account_number = account.text.strip()
        account_numbers.append(account_number)

    # Print the account numbers
    if print_info:
        print(account_numbers)
    divs = soup.find_all('div', {'class': 'flex flex-wrap w-full ng-star-inserted'})

    shareholders = []
    for div in divs:
        if 'shareholders' in div.text:
            for d in div.find_all('div', class_='authority-name ng-star-inserted'):
                name_span = d.find('span', {'class': 'ng-star-inserted'})
                name = name_span.text
                shareholders.append(name)
            if print_info:
                print(shareholders)

    return account_numbers, shareholders
