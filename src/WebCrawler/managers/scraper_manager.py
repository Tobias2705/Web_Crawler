from WebCrawler.input_validator import InputValidator
from WebCrawler.scrapers import *
from WebCrawler.sentiment import SentimentAnalyzer
from WebCrawler.custom_logger import get_logger

from threading import Thread
import pandas as pd
import os
import pathlib


class ScraperManager:
    def __init__(self, input_path, log_scrap_info=False):
        data, errors = InputValidator(input_path).validate_input()
        self.log_scrap_info = log_scrap_info
        self.data = data
        self.errors = errors

        self.logger = get_logger()

    def scrap(self):
        # run regon and krs scrapers parallelly
        regon_thread = Thread(target=self._run_regon_scraper)
        krs_thread = Thread(target=self._run_krs_scraper)

        self.logger.info('Starting scraping regon and krs')
        regon_thread.start()
        krs_thread.start()

        regon_thread.join()
        krs_thread.join()
        self.logger.info('Stopped scraping regon and krs')

        self.logger.info('Starting scraping stock names')
        self._run_stock_name_scraper()
        self.logger.info('Stopped scraping stock names')

        # run aleo, infostrefa and bankier parallelly
        aleo_thread = Thread(target=self._run_aleo_scraper)
        infostrefa_thread = Thread(target=self._run_infostrefa_scraper)
        bankier_thread = Thread(target=self._run_bankier_scraper)

        self.logger.info('Starting scraping aleo infostrefa and bankier')
        aleo_thread.start()
        infostrefa_thread.start()
        bankier_thread.start()

        aleo_thread.join()
        infostrefa_thread.join()
        bankier_thread.join()
        self.logger.info('Stopped scraping aleo infostrefa and bankier')

        sentiment_info_thread = Thread(target=self._run_info_sentiment)
        sentiment_bankier_thread = Thread(target=self._run_bankier_sentiment())
        sentiment_time_thread = Thread(target=self._run_time_scv())

        self.logger.info('Sentiment analysis started')
        sentiment_bankier_thread.start()
        sentiment_info_thread.start()
        sentiment_time_thread.start()

        sentiment_info_thread.join()
        sentiment_bankier_thread.join()
        sentiment_time_thread.join()
        self.logger.info('Sentiment analysis finished')

    def _run_aleo_scraper(self):
        # scraping from regon NIPs
        account_numbers_df = pd.DataFrame(columns=['nip', 'account_number'])
        shareholders_df = pd.DataFrame(columns=['nip', 'shareholder'])

        nips = self.regon_entity_df.nip.copy().drop_duplicates()

        for count, nip in enumerate(nips):
            counter = f'{str(count + 1)}/{len(nips)}'
            try:
                account_numbers, shareholders = get_href_links(nip)
                for account_number in account_numbers:
                    account_numbers_df.loc[len(account_numbers_df)] = [nip, account_number]

                for shareholder in shareholders:
                    shareholders_df.loc[len(shareholders_df)] = [nip, shareholder]

                if self.log_scrap_info:
                    self.logger.info(f"{counter} AleoScraper scraped: {nip}")
            except:
                if self.log_scrap_info:
                    self.logger.error(f"{counter} AleoScraper could not scrap: {nip}")

        self.aleo_account_numbers_df = account_numbers_df
        self.aleo_shareholders_df = shareholders_df

    def _run_info_sentiment(self):
        sentiment_analyzer = SentimentAnalyzer()
        self.info_sentiment = sentiment_analyzer.get_sentiment_analysis(self.infostrefa_news_df)

    def _run_bankier_sentiment(self):
        sentiment_analyzer = SentimentAnalyzer()
        self.bankier_sentiment = sentiment_analyzer.get_sentiment_analysis(self.bankier_news_df)

    def _run_time_scv(self):
        sentiment_analyzer = SentimentAnalyzer()

        info_time_df = sentiment_analyzer.generate_time_table(self.infostrefa_news_df)
        bank_time_df = sentiment_analyzer.generate_time_table(self.bankier_news_df)

        self.time_df = pd.concat([info_time_df, bank_time_df], ignore_index=True)

    def _run_stock_name_scraper(self):
        entities_df = self.regon_entity_df[["nazwa", "nip"]].copy().drop_duplicates()
        scraper = StockNameScraper(entities_df, print_info=self.log_scrap_info)
        stock_names = scraper.get_data()
        self.regon_entity_df['nazwa_gieldowa'] = stock_names

    def _run_infostrefa_scraper(self):
        # scraping from regon NIPs and names
        entities_df = self.regon_entity_df[["nip", "nazwa_gieldowa"]].copy().drop_duplicates()
        scraper = InfoStrefaScrapper(entities_df, print_info=self.log_scrap_info)
        self.infostrefa_news_df = scraper.get_data()

    def _run_bankier_scraper(self):
        # scraping from regon NIPs and names
        entities_df = self.regon_entity_df[["nip", "nazwa_gieldowa"]].copy().drop_duplicates()
        scraper = BankierScraper(entities_df, print_info=self.log_scrap_info)
        self.bankier_news_df = scraper.get_data()

    def _run_krs_scraper(self):
        general_info_df = pd.DataFrame(columns=[
            "nazwa", "krs", "nip", "regon", "forma_prawna", "data_wpisu_do_rej_przeds", "data_wykr_z_rej_przeds",
            "nazwa_org_repr", "sposob_repr", "adr_www", "email"])
        representants_df = pd.DataFrame()

        for count, row in enumerate(self.data):
            counter = f'{str(count + 1)}/{len(self.data)}'
            try:
                scraper = KrsScrapper(id=row[0], id_type=row[1])
                gen_info_dict, repr_df = scraper.scrap()

                representants_df = pd.concat([representants_df, repr_df], axis=0).reset_index(drop=True)
                general_info_df.loc[len(general_info_df)] = gen_info_dict.values()
                if self.log_scrap_info:
                    self.logger.info(f"{counter} KrsScraper scraped: {row}")
            except:
                if self.log_scrap_info:
                    self.logger.error(f"{counter} KrsScraper could not scrap: {row}")

        self.krs_representants_df = representants_df
        self.krs_general_info_df = general_info_df

    def _run_regon_scraper(self):
        regon_entity_df = pd.DataFrame()
        regon_local_entity_df = pd.DataFrame()
        regon_pkd = pd.DataFrame()

        regon_scraper = RegonScraper()

        for count, row in enumerate(self.data):
            counter = f'{str(count + 1)}/{len(self.data)}'
            try:
                e_df, l_df, p_df = regon_scraper.get_entity_info(row[0], row[1])
                regon_entity_df = pd.concat([regon_entity_df, e_df], axis=0).reset_index(drop=True)
                regon_local_entity_df = pd.concat([regon_local_entity_df, l_df], axis=0).reset_index(drop=True)
                regon_pkd = pd.concat([regon_pkd, p_df], axis=0).reset_index(drop=True)
                if self.log_scrap_info:
                    self.logger.info(f"{counter} RegonScrapper scraped: {row}")
            except:
                if self.log_scrap_info:
                    self.logger.error(f"{counter} RegonScrapper could not scrap: {row}")

        self.regon_entity_df = regon_entity_df
        self.regon_local_entity_df = regon_local_entity_df
        self.regon_pkd_df = regon_pkd

    def _get_results(self):
        return {'regon_entity_df': self.regon_entity_df.copy(), 'regon_local_entity_df': self.regon_local_entity_df.copy(), 'regon_pkd_df': self.regon_pkd_df.copy(), 'krs_representatives_df': self.krs_representants_df.copy(), 'krs_general_info_df': self.krs_general_info_df.copy(), 'aleo_account_numbers_df': self.aleo_account_numbers_df.copy(), 'aleo_shareholders_df': self.aleo_shareholders_df.copy(), 'infostrefa_news_df': self.infostrefa_news_df.copy(), 'bankier_news_df': self.bankier_news_df.copy(), 'sentiment_info_df': self.info_sentiment.copy(), 'sentiment_bankier_df': self.bankier_sentiment.copy(), 'time_df': self.time_df.copy()}

    def save_to_csv(self, path=''):
        for k, v in self._get_results().items():
            v.to_csv(os.path.join(path, k), index=False)


if __name__ == '__main__':

    input_path = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', '..', '..', 'examples', 'input.txt')
    manager = ScraperManager(input_path, log_scrap_info=True)
    manager.scrap()

    output_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', '..', '..', 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_dir = os.path.join(output_dir, 'csv')
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    manager.save_to_csv(path=csv_dir)
