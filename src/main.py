import pandas as pd
from input_validator.input_validator import InputValidator
from regon_scraper.regon_scraper import RegonScraper


def main():
    # Global variables
    regon_entity_df = pd.DataFrame()
    regon_local_entity_df = pd.DataFrame()
    regon_pkd = pd.DataFrame()

    # Components definition
    input_validator = InputValidator('input.txt')
    regon_scraper = RegonScraper()

    # Filtering input data
    data, errors = input_validator.validate_input()

    for row in data:
        e_df, l_df, p_df = regon_scraper.get_entity_info(row[0], row[1])

        regon_entity_df = pd.concat([regon_entity_df, e_df], axis=0).reset_index(drop=True)
        regon_local_entity_df = pd.concat([regon_local_entity_df, l_df], axis=0).reset_index(drop=True)
        regon_pkd = pd.concat([regon_pkd, p_df], axis=0).reset_index(drop=True)

    print(regon_entity_df)
    print(regon_local_entity_df)
    print(regon_pkd)


if __name__ == '__main__':
    main()
