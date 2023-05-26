# Osint Web Crawler

## Opis projektu

Projekt zrealizowany na przedmiot "Hurtownie Danych" ze współpracą z Komisją Nadzoru Finansowego.

W ramach projektu realizowane jest zbieranie danych na temat podmiotów, wpisów nt. tych podmiotów oraz analiza sentymentu wpisu.

Scrapowane strony:
- Regon - zbieranie podstawowych informacji o podmiocie
- KRS - zbieranie podstawowych informacji o podmiocie
- Aleo - zbieranie podstawowych informacji o podmiocie
- Bankier - wyciągane są depesze które podlegają ocenie sentymelnej
- Infostrefa - wyciągane są depesze które podlegają ocenie sentymelnej

## Instalacja

Przejdź do głównego folderu projektu i wykonaj następujące polecenie

```commandline
python -m pip install -e .
```

## Przykładowe komendy

Uruchomienie scrapowania:

```commandline
wcrawler file.txt -db -c
```
Flagi:
- db - zapisanie wyniku do bazy danych
- c - wyczyszczenie bazy danych przed jej użyciem

Uruchomienie graficznego klienta:
```commandline
wcrawler gui
```

## Autorzy

Tobiasz Gruszczyński,
Jakub Kaczmarek,
Miłosz Grocholewski,
Dan Brushko

