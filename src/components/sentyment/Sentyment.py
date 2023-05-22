import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
import pandas as pd

nltk.download('vader_lexicon')
nltk.download('wordnet')


def analyze_text(text):
    sentiment_dict = {
        "pozytywny": ["sukces", "wzrost", "postęp", "dobry", "wynik", "zwiększenie", "dobra", "tendencja", "doskonałe", "wynik", "wygrana", "przychód", "zysk", "dobrze", "prosperujący", "sukces", "rynkowy", "podwyższenie", "cena", "akcji"],
        "negatywny": ["spadek", "utrata", "niepowodzenie", "trudna", "sytuacja", "kłopoty", "strata", "złe", "wyniki", "przegrana", "strata", "dochodów", "koszty", "niewypłacalność", "upadek", "zły", "wynik", "finansowy"],
        "neutralny": ["zmiana", "nowe", "inwestycje", "nowy", "produkt", "przeprojektowanie", "rebranding", "nowa", "strategia", "połączenie", "inną", "firma", "nowy", "partner", "biznesowy", "zmiana", "zarządu"],
        "szansa": ["nowe", "możliwości", "perspektywy", "nowe", "rynki", "nowe", "trendy", "nowe", "technologie", "ekspansja", "nowi", "klienci", "nowy", "produkt", "rynku", "nowa", "lokalizacja"],
        "zagrożenie": ["ryzyko", "niewielkie", "szanse", "niedobrze", "rokujące", "prognozy", "spodziewane", "problemy", "kryzys", "ubezpieczenie", "przed", "ryzykiem", "niskie", "zyski"],
        "koszt": ["wydatki", "koszty", "podwyżki", "cen", "wysokie", "koszty", "niskie", "marże", "ograniczenie", "budżetu", "oszczędności", "redukcja", "kosztów"],
        "innowacja": ["nowe", "rozwiązania", "pionierskie", "pomysły", "nowoczesne", "technologie", "badania", "rozwój", "innowacyjne", "podejście", "dobre", "patenty"],
        "rynek": ["konkurencja", "nowi", "konkurenci", "nowi", "gracze", "rynku", "wzrost", "rywalizacji", "nowe", "produkty", "konkurentów", "nowe", "usługi", "rynku"],
    }

    analyzer = SentimentIntensityAnalyzer()
    lemmatizer = WordNetLemmatizer()
    text_lemmatized = ' '.join([lemmatizer.lemmatize(word) for word in text.split()])
    wynik = {'neg': 0.0, 'neu': 0.0, 'pos': 0.1, 'compound': 0.0}
    for word in text.split():
        for kategoria, keyword_list in sentiment_dict.items():
            if word in keyword_list or lemmatizer.lemmatize(word) in keyword_list:
                if kategoria == "innowacja":
                    wynik['pos'] += 0.05
                elif kategoria in ["negatywny", "koszt"]:
                    wynik['neg'] += 0.1
                elif kategoria == "neutralny":
                    wynik['neu'] += 0.1
                elif kategoria == "pozytywny":
                    wynik['pos'] += 0.1
                elif kategoria == "rynek":
                    wynik['neu'] += 0.05
                    wynik['neg'] += 0.05
                elif kategoria == "szansa":
                    wynik['pos'] += 0.05
                    wynik['neu'] += 0.05
                elif kategoria == "zagrożenie":
                    wynik['neg'] += 0.05
                    wynik['neu'] += 0.05
    label=max(wynik)
    if wynik[label]==0:
        return 'neutral'
    elif label == 'pos':
        if wynik['pos']>(wynik['neg']+wynik['neu'])*2:
            return 'positive'
        else:
            return 'slightly positive'
    elif label == 'neg':
        if wynik['neg']>(wynik['pos']+wynik['neu'])*2:
            return 'negative'
        else:
            return 'slightly negative'
    else:
        return 'neutral'

def generate_time_table(infostrefa_news_df):
    time_df = infostrefa_news_df.copy()
    time_df['Timestamp'] = pd.to_datetime(time_df['data'], format='%H:%M %d/%m/%Y')
    time_df['time_id'] = time_df['Timestamp'].dt.astype(str)
    time_df['godzina'] = time_df['Timestamp'].dt.hour
    time_df['dzien'] = time_df['Timestamp'].dt.day
    time_df['mesiac'] = time_df['Timestamp'].dt.month
    time_df['rok'] = time_df['Timestamp'].dt.year
    time_df=time_df[['time_id','dzien','mesiac','rok','godzina']]
    return time_df
def get_sentyment_analysis(infostrefa_news_df):
    sentyment_df=infostrefa_news_df.copy()
    sentyment_df['Timestamp'] = pd.to_datetime(sentyment_df['data'], format='%H:%M %d/%m/%Y')
    sentyment_df['Time_id'] = sentyment_df['Timestamp'].dt.astype(str)
    sentyment_df['typ_oceny']=sentyment_df['wiadomosc'].apply(lambda x:analyze_text(x))
    sentyment_df=sentyment_df.rename(columns={'spolka':'nip'})
    sentyment_df=sentyment_df[['nip','typ_oceny']]
    return sentyment_df