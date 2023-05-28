import nltk
from nltk.stem import WordNetLemmatizer
import pandas as pd

nltk.download('vader_lexicon', quiet=True)
nltk.download('wordnet', quiet=True)


class SentimentAnalyzer:
    def __init__(self):
        self.sentiment_dict = {
            "pozytywny": ["sukces", "wzrost", "postęp", "dobry", "wynik", "zwiększenie", "dobra", "tendencja",
                          "doskonałe", "wynik", "wygrana", "przychód", "zysk", "dobrze", "prosperujący", "sukces",
                          "rynkowy", "podwyższenie", "cena", "akcji"],
            "negatywny": ["spadek", "utrata", "niepowodzenie", "trudna", "sytuacja", "kłopoty", "strata", "złe",
                          "wyniki", "przegrana", "strata", "dochodów", "koszty", "niewypłacalność", "upadek", "zły",
                          "wynik", "finansowy"],
            "neutralny": ["zmiana", "nowe", "inwestycje", "nowy", "produkt", "przeprojektowanie", "rebranding", "nowa",
                          "strategia", "połączenie", "inną", "firma", "nowy", "partner", "biznesowy", "zmiana",
                          "zarządu"],
            "szansa": ["nowe", "możliwości", "perspektywy", "nowe", "rynki", "nowe", "trendy", "nowe", "technologie",
                       "ekspansja", "nowi", "klienci", "nowy", "produkt", "rynku", "nowa", "lokalizacja"],
            "zagrożenie": ["ryzyko", "niewielkie", "szanse", "niedobrze", "rokujące", "prognozy", "spodziewane",
                           "problemy", "kryzys", "ubezpieczenie", "przed", "ryzykiem", "niskie", "zyski"],
            "koszt": ["wydatki", "koszty", "podwyżki", "cen", "wysokie", "koszty", "niskie", "marże", "ograniczenie",
                      "budżetu", "oszczędności", "redukcja", "kosztów"],
            "innowacja": ["nowe", "rozwiązania", "pionierskie", "pomysły", "nowoczesne", "technologie", "badania",
                          "rozwój", "innowacyjne", "podejście", "dobre", "patenty"],
            "rynek": ["konkurencja", "nowi", "konkurenci", "nowi", "gracze", "rynku", "wzrost", "rywalizacji", "nowe",
                      "produkty", "konkurentów", "nowe", "usługi", "rynku"],
        }
        self.lemmatizer = WordNetLemmatizer()

    def analyze_text(self, text):
        result = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
        for word in text.split():
            for category, keyword_list in self.sentiment_dict.items():
                if word in keyword_list or self.lemmatizer.lemmatize(word) in keyword_list:
                    if category == "innowacja":
                        result['pos'] += 0.05
                    elif category in ["negatywny", "koszt"]:
                        result['neg'] += 0.1
                    elif category == "neutralny":
                        result['neu'] += 0.1
                    elif category == "pozytywny":
                        result['pos'] += 0.1
                    elif category == "rynek":
                        result['neu'] += 0.05
                        result['neg'] += 0.05
                    elif category == "szansa":
                        result['pos'] += 0.05
                        result['neu'] += 0.05
                    elif category == "zagrożenie":
                        result['neg'] += 0.05
                        result['neu'] += 0.05

        label = max(result)
        if result[label] == 0:
            return 'neutralny'
        elif label == 'pos':
            if result['pos'] > (result['neg'] + result['neu']) * 2:
                return 'pozytywny'
            else:
                return 'częściowo pozytywny'
        elif label == 'neg':
            if result['neg'] > (result['pos'] + result['neu']) * 2:
                return 'negatywny'
            else:
                return 'częściowo negatywny'
        else:
            return 'neutralny'

    def generate_time_table(self, df):
        time_df = pd.DataFrame()
        timestamp = pd.to_datetime(df['data'], format='%H:%M %d/%m/%Y')

        time_df['godzina'] = timestamp.dt.hour
        time_df['dzien'] = timestamp.dt.day
        time_df['miesiac'] = timestamp.dt.month
        time_df['rok'] = timestamp.dt.year

        return time_df

    def get_sentiment_analysis(self, df):
        sentiment_analysis = df.copy()
        timestamp = pd.to_datetime(df['data'], format='%H:%M %d/%m/%Y')

        sentiment_analysis['timestamp'] = timestamp.astype(str)
        sentiment_analysis['typ_oceny'] = sentiment_analysis['wiadomosc'].apply(lambda x: self.analyze_text(x))
        sentiment_analysis = sentiment_analysis.rename(columns={'spolka': 'nip'})
        sentiment_analysis = sentiment_analysis[['nip', 'typ_oceny', 'timestamp']]

        return sentiment_analysis
