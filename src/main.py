import os
from component_1 import RegonDatabaseScrapper

input_data_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'input_data'))
test_data_path = os.path.join(input_data_path, 'test_data.txt')
scraper = RegonDatabaseScrapper(test_data_path)
scraper.get_entity_info()
