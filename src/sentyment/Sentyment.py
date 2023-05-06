#!/usr/bin/env python
# coding: utf-8

# In[11]:


import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer

nltk.download('vader_lexicon')
nltk.download('wordnet')


def main(text):
    sentiment_dict = {
        "pozytywny": ["sukces", "wzrost", "postęp", "dobry wynik", "zwiększenie", "dobra tendencja", "doskonałe wyniki", "wygrana", "przychód", "zysk", "dobrze prosperujący", "sukces rynkowy", "podwyższenie ceny akcji"],
        "negatywny": ["spadek", "utrata", "niepowodzenie", "trudna sytuacja", "kłopoty", "strata", "złe wyniki", "przegrana", "strata dochodów", "koszty", "niewypłacalność", "upadek", "zły wynik finansowy"],
        "neutralny": ["zmiana", "nowe inwestycje", "nowy produkt", "przeprojektowanie", "rebranding", "nowa strategia", "połączenie z inną firmą", "nowy partner biznesowy", "zmiana zarządu"],
        "szansa": ["nowe możliwości", "perspektywy", "nowe rynki", "nowe trendy", "nowe technologie", "ekspansja", "nowi klienci", "nowy produkt na rynku", "nowa lokalizacja"],
        "zagrożenie": ["ryzyko", "niewielkie szanse", "niedobrze rokujące prognozy", "spodziewane problemy", "kryzys", "ubezpieczenie przed ryzykiem", "niskie zyski"],
        "koszt": ["wydatki", "koszty", "podwyżki cen", "wysokie koszty", "niskie marże", "ograniczenie budżetu", "oszczędności", "redukcja kosztów"],
        "innowacja": ["nowe rozwiązania", "pionierskie pomysły", "nowoczesne technologie", "badania i rozwój", "innowacyjne podejście", "dobre patenty"],
        "rynek": ["konkurencja", "nowi konkurenci", "nowi gracze na rynku", "wzrost rywalizacji", "nowe produkty konkurentów", "nowe usługi na rynku"],
    }

    analyzer = SentimentIntensityAnalyzer()
    lemmatizer = WordNetLemmatizer()
    text_lemmatized = ' '.join([lemmatizer.lemmatize(word) for word in text.split()])
    result = analyzer.polarity_scores(text_lemmatized)
    wynik = analyzer.polarity_scores(text)
    for word in text.split():
        for category, keyword_list in sentiment_dict.items():
            if word in keyword_list or lemmatizer.lemmatize(word) in keyword_list:
                if kategoria == "pozytywny":
                    wynik['pos'] += 0.1
                elif kategoria == "negatywny":
                    wynik['neg'] += 0.1
                elif kategoria == "neutralny":
                    wynik['neu'] += 0.1
                elif kategoria == "szansa":
                    wynik['pos'] += 0.05
                    wynik['neu'] += 0.05
                elif kategoria == "zagrożenie":
                    wynik['neg'] += 0.05
                    wynik['neu'] += 0.05
                elif kategoria == "koszt":
                    wynik['neg'] += 0.1
                elif kategoria == "innowacja":
                    wynik['pos'] += 0.05
                elif kategoria == "rynek":
                    wynik['neu'] += 0.05
                    wynik['neg'] += 0.05
    print("Wynik analizy sentymentu: ", wynik['compound'])
    print(result)
    print(wynik)

