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
