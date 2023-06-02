import os
import warnings
import nltk
import pandas as pd
import torch
from nltk.stem import WordNetLemmatizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

nltk.download('vader_lexicon', quiet=True)
nltk.download('wordnet', quiet=True)


class SentimentAnalyzer:
    """
    A class used to analyze sentiment in text data.

    ...

    Attributes
    ----------
    sentiment_dict : dict
        A dictionary containing lists of words associated with different sentiment categories.
    lemmatizer : WordNetLemmatizer
        An instance of the WordNetLemmatizer class.
    tokenizer : AutoTokenizer
        An instance of the AutoTokenizer class.
    model : AutoModelForSequenceClassification
        An instance of the AutoModelForSequenceClassification class.

    Methods
    -------
    analyze_text(text)
        Analyzes the sentiment of the given text and returns the sentiment category.
    generate_time_table(df)
        Generates a time's table from the given DataFrame.
    get_sentiment_analysis(df)
        Analyzes the sentiment of the text data in the given DataFrame and returns a DataFrame with sentiment analysis
        results.
    """
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
        warnings.filterwarnings("ignore")
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        self.lemmatizer = WordNetLemmatizer()
        model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def analyze_text(self, text: str) -> str:
        """
        Analyzes the sentiment of the given text and returns the sentiment category.

        Parameters
        ----------
        text : str
            The text to be analyzed.

        Returns
        -------
        str
            The sentiment category of the text (either "negatwny", "neutralny", or "pozytywny").
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)
        sentiment = torch.argmax(outputs.logits, dim=1).item()

        if sentiment == 0:
            return "negatwny"
        elif sentiment == 1:
            return "neutralny"
        else:
            return "pozytywny"

    @staticmethod
    def generate_time_table(df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates a data for time's table from the given DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            The input DataFrame.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the time's table.
        """
        time_df = pd.DataFrame()

        timestamp = pd.to_datetime(df['data'], format='%H:%M %d/%m/%Y')

        time_df['godzina'] = timestamp.dt.hour
        time_df['dzien'] = timestamp.dt.day
        time_df['miesiac'] = timestamp.dt.month
        time_df['rok'] = timestamp.dt.year

        return time_df

    def get_sentiment_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyzes the sentiment of the text data in the given DataFrame and returns a DataFrame with sentiment analysis
        results.

        Parameters
        ----------
        df : pd.DataFrame
            The input DataFrame containing text data to be analyzed.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the sentiment analysis results.
        """
        sentiment_analysis = df.copy()

        timestamp = pd.to_datetime(df['data'], format='%H:%M %d/%m/%Y')

        sentiment_analysis['timestamp'] = timestamp.astype(str)
        sentiment_analysis['typ_oceny'] = sentiment_analysis['wiadomosc'].apply(lambda x: self.analyze_text(x))
        sentiment_analysis = sentiment_analysis.rename(columns={'spolka': 'nip'})
        sentiment_analysis = sentiment_analysis[['nip', 'typ_oceny', 'timestamp']]

        return sentiment_analysis
