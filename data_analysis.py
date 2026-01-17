import pandas as pd


def load_data(filepath='pm25_cleaned.csv'):
    """Wczytuje dane z pliku CSV."""
    df = pd.read_csv(filepath, low_memory=False)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    return df


def calculate_daily_stats(df, norm_threshold=15):
    """Oblicza średnie dobowe i sprawdza przekroczenia normy."""
    df['data_dzien'] = df['data'].dt.floor('D')

    daily = (
        df.groupby(['Miejscowość', 'kod_stacji', 'data_dzien'])['pm25']
        .mean()
        .round(2)
        .reset_index()
    )

    daily.rename(columns={'pm25': 'pm25_srednia_dobowa'}, inplace=True)
    daily['przekroczenie_normy'] = daily['pm25_srednia_dobowa'] >= norm_threshold

    return daily

def calculate_monthly_stats(df):
    """Oblicza średnie miesięczne."""
    df['rok'] = df['data'].dt.year.astype('Int64')
    df['miesiac'] = df['data'].dt.month

    total_measurements = len(df)

    monthly = (
        df.groupby(['Miejscowość', 'kod_stacji', 'rok', 'miesiac'])['pm25']
        .mean()
        .round(2)
        .reset_index()
    )

    monthly.rename(columns={'pm25': 'pm25_srednia_miesieczna'}, inplace=True)

    return monthly

def merge_stats(df, daily, monthly):
    """Łączy średnie dobowe i miesięczne z oryginalnym DataFrame."""
    # Klucze czasowe
    df['data_dzien'] = df['data'].dt.floor('D')
    df['rok'] = df['data'].dt.year.astype('Int64')
    df['miesiac'] = df['data'].dt.month

    # Merge średnich dobowych
    df = df.merge(
        daily,
        on=['Miejscowość', 'kod_stacji', 'data_dzien'],
        how='left'
    )

    # Merge średnich miesięcznych
    df = df.merge(
        monthly,
        on=['Miejscowość', 'kod_stacji', 'rok', 'miesiac'],
        how='left'
    )

    return df

def save_to_csv(df, filepath='pm25_cleaned.csv'):
    df.to_csv(filepath, index=False)

def get_voivodeship_mapping(df_metadata):
    """Tworzy mapowanie kodów stacji na województwa."""
    if 'Kod stacji' in df_metadata.columns and 'Województwo' in df_metadata.columns:
        df_metadata['Województwo'] = df_metadata['Województwo'].str.capitalize()
        station_to_voivodeship = df_metadata.set_index('Kod stacji')['Województwo'].to_dict()
        return station_to_voivodeship
    else:
        raise KeyError("Brak kolumny 'Kod stacji' lub 'Województwo' w metadanych")