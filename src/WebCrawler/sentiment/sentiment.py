import nltk
from nltk.stem import WordNetLemmatizer
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

nltk.download('vader_lexicon', quiet=True)
nltk.download('wordnet', quiet=True)


class SentimentAnalyzer:
    def __init__(self, analyze_bankier=False):
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
        self.analyze_bankier = analyze_bankier
        model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def analyze_text(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)
        sentiment = torch.argmax(outputs.logits, dim=1).item()

        if sentiment == 0:
            return "negatwny"
        elif sentiment == 1:
            return "neutralmy"
        else:
            return "pozytywny"

    def generate_time_table(self, df):
        time_df = pd.DataFrame()

        if self.analyze_bankier:
            timestamp = pd.to_datetime(df['data'], format='%Y-%m-%d %H:%M')
        else:
            timestamp = pd.to_datetime(df['data'], format='%H:%M %d/%m/%Y')

        time_df['godzina'] = timestamp.dt.hour
        time_df['dzien'] = timestamp.dt.day
        time_df['miesiac'] = timestamp.dt.month
        time_df['rok'] = timestamp.dt.year

        return time_df

    def get_sentiment_analysis(self, df):
        sentiment_analysis = df.copy()

        if self.analyze_bankier:
            timestamp = pd.to_datetime(df['data'], format='%Y-%m-%d %H:%M')
        else:
            timestamp = pd.to_datetime(df['data'], format='%H:%M %d/%m/%Y')

        sentiment_analysis['timestamp'] = timestamp.astype(str)
        sentiment_analysis['typ_oceny'] = sentiment_analysis['wiadomosc'].apply(lambda x: self.analyze_text(x))
        sentiment_analysis = sentiment_analysis.rename(columns={'spolka': 'nip'})
        sentiment_analysis = sentiment_analysis[['nip', 'typ_oceny', 'timestamp']]

        return sentiment_analysis
