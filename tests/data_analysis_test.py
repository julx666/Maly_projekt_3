import pytest
import pandas as pd
import sys
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby importować moduły
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_analysis import *


def test_calculate_daily_stats():
    """Testuje obliczanie średnich dobowych i wykrywanie przekroczeń normy."""
    df = pd.DataFrame({
        "Miejscowość": ["Warszawa", "Warszawa"],
        "kod_stacji": ["S1", "S1"],
        "data": pd.to_datetime(["2020-01-01 01:00", "2020-01-01 12:00"]),
        "pm25": [10, 20]
    })

    daily = calculate_daily_stats(df, norm_threshold=15)

    assert daily.iloc[0]["pm25_srednia_dobowa"] == 15  # średnia z 10 i 20
    assert daily.iloc[0]["przekroczenie_normy"] == True


def test_calculate_monthly_stats():
    """Testuje obliczanie średnich miesięcznych."""
    df = pd.DataFrame({
        "Miejscowość": ["Katowice", "Katowice"],
        "kod_stacji": ["S2", "S2"],
        "data": pd.to_datetime(["2020-02-01 01:00", "2020-02-15 12:00"]),
        "pm25": [30, 50]
    })

    monthly = calculate_monthly_stats(df)

    assert monthly.iloc[0]["pm25_srednia_miesieczna"] == 40  # średnia z 30 i 50