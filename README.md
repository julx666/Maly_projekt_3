# Maly_projekt_3
## Notebooki
###maly_projekt_1_fixed.ipynb
Pobiera i czyści dane, oblicza statystyki, rysuje wykresy:
* Wykres średniego miesięcznego stężenia PM2.5 dla Warszawy i Katowic w latach 2015 i 2024. 
* Heatmapy średnich miesięcznych dla wybranych miast w latach 2015, 2018, 2021, 2024.
* Wykres słupkowy dni z przekroczeniem normy PM2.5 dla najmniej zanieczyszczonych i najbardziej zanieczyszczonych stacji w latach 2015, 2018, 2021, 2024.


## Moduły
### read_and_clean_data.py
Definiuje funkcje do pobierania i czyszczenia danych pomiarowych oraz metadanych z powietrze.gios.gov.pl.

### data_analysis.py
Definiuje funkcje do analizy oczyszczonych danych: obliczania statystyk dobowych, miesięcznych, przekroczeń normy. 

### visualizations.py
Definiuje funkcje do rysowania: wykresu średnich miesięcznych wartości PM2.5 dla wybranych miast i lat, heatmapy średnich miesięcznych wartości PM2.5 dla wszystkich miejscowości, wykresu słupkowego liczby dni z przekroczeniem normy PM2.5 dla najlepszych i najgorszych stacji.

## Testy
### read_and_clean_data_test.py
Testuje funkcje z *read_and_clean_data.py* do pobierania i czyszczenia danych.

### data_analysis_test.py
Testuje funkcje z *data_analysis.py* do analizy oczyszcoznych danych.

### visualizations_test.py
Testuje funkcje z *visualizations.py* do rysowania wykresów.

## Pliki
### pm25_cleaned.csv
Plik z oczyszczonymi danymi. 
