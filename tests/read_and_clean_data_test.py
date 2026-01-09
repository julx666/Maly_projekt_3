import pytest
import pandas as pd
import sys
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby importować moduły
sys.path.insert(0, str(Path(__file__).parent.parent))

from read_and_clean_data import *


def test_find_data_start_row():
    """Testuje poprawne wykrycie początku danych pomiarowych"""
    df = pd.DataFrame({
        0: [
            "Nagłówek",
            "Coś innego",
            "2020-01-01 01:00:00",
            "2020-01-01 02:00:00"
        ]
    })

    assert find_data_start_row(df) == 2


def test_filter_rows_by_content():
    """Testuje filtrowanie wierszy na podstawie zawartości"""
    df = pd.DataFrame({
        0: [
            "Kod stanowiska",
            "Jednostka",
            "2020-01-01 01:00:00"
        ],
        1: ["X", "Y", 10]
    })

    filtered = filter_rows_by_content(df, year=2021)

    assert len(filtered) == 1
    assert filtered.iloc[0, 0] == "2020-01-01 01:00:00"


def test_get_common_stations():
    """Testuje znalezienie wspólnych stacji dla wszystkich lat"""
    data = {
        2015: pd.DataFrame({"kod_stacji": ["A", "B", "C"]}),
        2018: pd.DataFrame({"kod_stacji": ["B", "C", "D"]}),
        2021: pd.DataFrame({"kod_stacji": ["C", "B"]}),
        2024: pd.DataFrame({"kod_stacji": ["B", "C", "E"]})
    }

    assert get_common_stations(data) == {"B", "C"}


def test_clean_data_basic_flow():
    """Testuje podstawowy przepływ funkcji clean_data"""
    df = pd.DataFrame({
        0: ["Kod stanowiska", "ST001", "2020-01-01 01:00:00"],
        1: ["-", "ST002", 25]
    })

    metadata = pd.DataFrame({
        "Kod stacji": ["ST002"],
        "Miejscowość": ["Warszawa"]
    })

    result = clean_data(df, year=2020, df_metadata=metadata)

    assert not result.empty
    assert set(result.columns) == {"Miejscowość", "kod_stacji", "data", "pm25"}
    assert result.iloc[0]["pm25"] == 25

