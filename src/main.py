import os
from component_1 import RegonDatabaseScrapper

input_data_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'input_data'))
test_data_path = os.path.join(input_data_path, 'test_data.txt')
scraper = RegonDatabaseScrapper(test_data_path)

regon_db, regon_local_db = scraper.get_entity_info()
print(regon_db[['nip', 'regon', 'nazwa', 'wojewodztwo']])
print(regon_local_db[['regon', 'regon j.nadrzędnej', 'nip j.nadrzędnej', 'nazwa']])
