import pandas as pd
import requests
import zipfile
import io
import re


def download_gios_archive(year, config, gios_archive_url="https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"):
    """Pobiera archiwum ZIP z danymi pomiarowymi dla danego roku."""
    archive_id = config['archive_id']
    filename = config['pm25_filename']
    
    # Pobranie archiwum ZIP do pamięci
    url = f"{gios_archive_url}{archive_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # jeśli błąd HTTP, zatrzymaj
        
        # Otwórz zip w pamięci
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Sprawdź czy plik istnieje w archiwum
            if filename not in z.namelist():
                print(f"Ostrzeżenie: Plik {filename} nie znaleziony w archiwum.")
                print(f"Dostępne pliki: {z.namelist()[:5]}...")  # pokaż pierwsze 5
                return None
            
            # wczytaj plik do pandas
            with z.open(filename) as f:
                df = pd.read_excel(f, header=None)
                
        print(f"Dane dla roku {year} pobrane pomyślnie")
        return df
        
    except Exception as e:
        print(f"Błąd przy pobieraniu danych dla roku {year}: {e}")
        return None


def download_metadata(metadata_url="https://powietrze.gios.gov.pl/pjp/archives/downloadFile/622"):
    """Pobiera metadane i zwraca je jako DataFrame."""
    try:
        response = requests.get(metadata_url)
        response.raise_for_status()  # jeśli błąd HTTP, zatrzymaj
        
        # Wczytaj metadane jako DataFrame
        df = pd.read_excel(io.BytesIO(response.content))
        print(f"Metadane pobrane pomyślnie: {df.shape[0]} wierszy, {df.shape[1]} kolumn")
        
        return df
    except Exception as e:
        print(f"Błąd przy pobieraniu metadanych: {e}")
        return None


def find_data_start_row(df):
    """Znajduje wiersz, w którym zaczynają się dane pomiarowe z datami."""
    date_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    
    for idx in range(len(df)):
        first_cell = str(df.iloc[idx, 0])
        if re.match(date_pattern, first_cell):
            return idx
    
    return None


def filter_rows_by_content(df, year):
    """
    Filtruje wiersze na podstawie zawartości zamiast indeksów.
    Usuwa niepotrzebne wiersze
    """
    df = df.copy()
    
    # Szukamy wzorców w pierwszej kolumnie
    patterns_to_remove = [
        r'Kod stanowiska',  
        r'Jednostka',
        r'Nr',  
        r'Wskaźnik',
        r'Czas uśredniania'          
    ]
    
    rows_to_keep = []
    
    for idx in range(len(df)):
        cell_value = str(df.iloc[idx, 0])
        should_keep = True
        
        # Sprawdzamy czy wiersz zawiera coś co chcemy usunąć
        for pattern in patterns_to_remove:
            if re.search(pattern, cell_value, re.IGNORECASE):
                should_keep = False
                break
        
        # Dodatkowo dla roku 2014 mogą być inne specyficzne wzorce
        if year == 2014 and re.search(r'^\s*PM2.5', cell_value):
            should_keep = False
        
        if should_keep:
            rows_to_keep.append(idx)
    
    df_filtered = df.iloc[rows_to_keep].copy()
    df_filtered = df_filtered.reset_index(drop=True)
    
    print(f"Po filtracji: {len(df_filtered)} wierszy (usunięto {len(df) - len(df_filtered)})")
    return df_filtered


def clean_data(df, year, df_metadata):
    '''
    Czyści dane pomiarowe PM2.5 i przekształca do formatu długiego.
    
    Parametry:
    df - dane z pomiarami
    year - rok danych
    df_metadata - metadane ze stacjami
    '''
    # Filtracja wierszy na podstawie zawartości
    df_filtered = filter_rows_by_content(df, year)
    
    # znajdź wiersz, w którym zaczynają się dane pomiarowe (z datami)
    data_start_row = find_data_start_row(df_filtered)
    
    if data_start_row is None:
        raise ValueError(f"Nie znaleziono wierszy z datami w pliku dla roku {year}")
    
    # Przygotuj nagłówki kolumn
    # Zakładamy że kody stacji są w wierszu 0 (pierwszy wiersz po filtracji)
    station_codes = df_filtered.iloc[0, 1:].tolist()  # Pomijamy pierwszą kolumnę
    new_columns = ['data'] + [str(code).strip() for code in station_codes]
    
    # Wybierz tylko dane pomiarowe (od wiersza z datami)
    data_df = df_filtered.iloc[data_start_row:].copy()
    data_df = data_df.reset_index(drop=True)
    
    # Przypisz nowe nazwy kolumn
    data_df.columns = new_columns[:len(data_df.columns)]
    
    # Rozwiń dane do formatu długiego
    df_long = data_df.melt(id_vars=['data'], var_name='kod_stacji', value_name='pm25')
    
    # Aktualizuj stare kody stacji na podstawie metadanych
    if 'Stary Kod stacji \n(o ile inny od aktualnego)' in df_metadata.columns and 'Kod stacji' in df_metadata.columns:
        station_mapping = {}
        
        for _, row in df_metadata.iterrows():
            old_codes = row['Stary Kod stacji \n(o ile inny od aktualnego)']
            new_code = str(row['Kod stacji']).strip()
            
            if pd.notna(old_codes) and str(old_codes).strip() != '':
                old_code_list = str(old_codes).split(',')
                
                for old_code in old_code_list:
                    old_code_clean = old_code.strip()
                    if old_code_clean:
                        station_mapping[old_code_clean] = new_code
        
        print(f"Rok {year}: Utworzono mapowanie dla {len(station_mapping)} starych kodów stacji")
        
        df_long['kod_stacji'] = df_long['kod_stacji'].map(
            lambda x: station_mapping.get(str(x).strip(), str(x).strip())
        )
    else:
        print(f"Ostrzeżenie dla roku {year}: Brak kolumn do mapowania starych kodów stacji")
    
    # Konwersja typów danych
    df_long['data'] = pd.to_datetime(df_long['data'], errors='coerce')
    df_long['pm25'] = pd.to_numeric(
        df_long['pm25'].astype(str).str.replace(',', '.'), 
        errors='coerce'
    )
    
    # Dodaj miejscowość z metadanych
    if 'Kod stacji' in df_metadata.columns and 'Miejscowość' in df_metadata.columns:
        station_to_city = df_metadata.set_index('Kod stacji')['Miejscowość'].to_dict()
        df_long['Miejscowość'] = df_long['kod_stacji'].map(station_to_city)
        
        # Sprawdź brakujące mapowania
        missing_count = df_long['Miejscowość'].isna().sum()
        if missing_count > 0:
            missing_stations = df_long[df_long['Miejscowość'].isna()]['kod_stacji'].unique()
            print(f"Ostrzeżenie rok {year}: Brak miejscowości dla {len(missing_stations)} stacji {missing_stations}")
    else:
        raise KeyError("Brak kolumn 'Kod stacji' lub 'Miejscowość' w metadanych")
    
    # Korekta pomiarów z godziny 00:00
    midnight_mask = df_long['data'].dt.hour == 0
    df_long.loc[midnight_mask, 'data'] = df_long.loc[midnight_mask, 'data'] - pd.Timedelta(days=1)
    
    # Posprzątaj kolumny
    final_columns = ['Miejscowość', 'kod_stacji', 'data', 'pm25']
    df_long = df_long[final_columns]
    
    # Statystyki końcowe
    unique_days = df_long['data'].dt.date.nunique()
    print(f"{len(df_long)} pomiarów, {unique_days} dni, {df_long['kod_stacji'].nunique()} stacji")
    
    return df_long


def get_common_stations(data_dict):
    """Znajduje wspólne stacje dla wszystkich lat."""
    common_stations = None
    
    for year, df in data_dict.items():
        stations = set(df['kod_stacji'].unique())
        
        if common_stations is None:
            common_stations = stations
        else:
            common_stations = common_stations.intersection(stations)
    
    if common_stations is None:
        return set()
    
    print(f"Znaleziono {len(common_stations)} wspólnych stacji dla wszystkich lat")
    return common_stations


def save_cleaned_data(df_all, output_path='pm25_cleaned.csv'):
    """Zapisuje oczyszczone dane do pliku CSV."""
    df_all = df_all.set_index(['Miejscowość', 'kod_stacji']).sort_index()
    df_all.to_csv(output_path)
    print(f"Dane zapisane do: {output_path}")
    return output_path
