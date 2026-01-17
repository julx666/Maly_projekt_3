import matplotlib
matplotlib.use('Agg') #Włącza non-interactive mode w matplotlibie, zapobiega niepożądanym błędom wynikającym z niekompatybilności windows/linux 

import pytest
import pandas as pd
import sys
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby importować moduły
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualizations import *


def test_plot_monthly_trends(monkeypatch):
    """Testuje, czy funkcja plot_monthly_trends działa."""
    df = pd.DataFrame({
        "Miejscowość": ["Warszawa", "Katowice", "Gdańsk"],
        "rok": [2015, 2024, 2024],
        "miesiąc": [1, 2, 3],
        "pm25_srednia_miesieczna": [10, 20, 15],
        "data": pd.to_datetime(["2015-01-01", "2024-02-01", "2024-03-01"])
    })

    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None) # Zapobiega wyświetlaniu wykresu podczas testu

    plot_monthly_trends(df)  # test przejdzie jeśli nie rzuci wyjątku


def test_heatmaps_runs(monkeypatch):
    """Testuje, czy funkcja heatmaps działa."""
    df = pd.DataFrame({
        "Miejscowość": ["Warszawa", "Katowice"],
        "kod_stacji": ["S1", "S2"],
        "rok": [2015, 2024],
        "miesiąc": [1, 2],
        "pm25_srednia_miesieczna": [12, 18],
        "data": pd.to_datetime(["2015-01-01", "2024-02-01"])
    })

    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None) # Zapobiega wyświetlaniu wykresu podczas testu
    heatmaps(df)


def test_days_over_norm_runs(monkeypatch):
    """Testuje, czy funkcja days_over_norm działa."""
    df = pd.DataFrame({
        "Miejscowość": ["Warszawa", "Katowice", "Warszawa"],
        "kod_stacji": ["S1", "S2", "S3"],
        "rok": [2024, 2024, 2024],
        "przekroczenie_normy": [True, True, False],
        "data": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    })

    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None) # Zapobiega wyświetlaniu wykresu podczas testu
    days_over_norm(df)

def test_days_over_norm_by_voivodeship(monkeypatch):
    """Testuje, czy funkcja days_over_norm_by_voivodeship działa i wyświetla poprawne województwa."""
    valid_list = {
        'Dolnośląskie', 'Kujawsko-pomorskie', 'Lubelskie', 'Łódzkie', 'Lubuskie',
        'Małopolskie', 'Mazowieckie', 'Opolskie', 'Podlaskie', 'Podkarpackie',
        'Pomorskie', 'Świętokrzyskie', 'Śląskie', 'Warmińsko-mazurskie',
        'Wielkopolskie', 'Zachodniopomorskie'
    }

    df_meta = pd.DataFrame({'Kod stacji': ['S1'], 'Województwo': ['Śląskie']})
    df = pd.DataFrame({
        "kod_stacji": ['S1'], "rok": [2024], "przekroczenie_normy": [True],
        "data_dzien": ["2024-01-01"] 
    })

    def check_values(data, **kwargs): #sprawdza czy w pierwszej kolumnie podanej do plotowania województwa są poprawne
        values = data.iloc[:, 0].unique()
        
        for name in values:
            if name not in valid_list:
                raise AssertionError(f"invalid Województwo: {name}")
                
        return plt.gca()

    monkeypatch.setattr("seaborn.barplot", check_values)
    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None)
    monkeypatch.setattr("matplotlib.pyplot.legend", lambda: None)
    
    days_over_norm_by_voivodeship(df, df_meta)