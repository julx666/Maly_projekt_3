import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colormaps
import seaborn as sns
from data_analysis import get_voivodeship_mapping


def plot_monthly_trends(df):
    """Rysuje wykres średnich miesięcznych wartości PM2.5 dla wybranych miast i lat."""
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    
    # Wyodrębnij rok i miesiąc
    df['rok'] = df['data'].dt.year
    df['miesiąc'] = df['data'].dt.month

    # Wyciągnij dane tylko dla wybranych miast i lat
    filtered_data = df[
        (df['Miejscowość'].isin(['Warszawa', 'Katowice'])) &
        (df['rok'].isin([2015, 2024]))
    ]
    
    # Oblicz średnie miesięczne wartości PM2.5
    cities_avg = filtered_data.groupby(['Miejscowość', 'rok', 'miesiąc'])['pm25_srednia_miesieczna'].mean().reset_index()
    
    # Przygotowanie wykresu
    plt.figure(figsize=(12,6))

    for city in ['Warszawa', 'Katowice']:
        for year in [2015, 2024]:
            # Filtruj dane dla danej kombinacji
            data = cities_avg[
                (cities_avg['Miejscowość'] == city) & 
                (cities_avg['rok'] == year)
            ].sort_values('miesiąc')

            if not data.empty:
                # Rysuj linie
                plt.plot(data['miesiąc'], data['pm25_srednia_miesieczna'], label=f'{city} {year}', linewidth=3)

    plt.xlabel('Miesiąc', weight='bold')
    plt.ylabel('Średnie stężenie PM2.5 (μg/m^3)', weight='bold')
    plt.title('Średnie miesięczne stężenie PM2.5: Warszawa, Katowice', weight='bold', fontsize=16)
    plt.legend()
    plt.tight_layout()
    plt.show()



def heatmaps(df):
    """Rysuje heatmapy średnich miesięcznych wartości PM2.5 dla wszystkich miejscowości."""
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    
    # Wyodrębnij rok i miesiąc
    df['rok'] = df['data'].dt.year
    df['miesiąc'] = df['data'].dt.month

    # Uzyj wcześniej obliczonych średnich miesięcznych (weź pierwszą wartość, ponieważ wszystkie w tej samej grupie mają tę samą wartość)
    monthly_avg = df.groupby([
        'Miejscowość', 
        'kod_stacji', 
        'rok',
        'miesiąc'
    ])['pm25_srednia_miesieczna'].first().reset_index()
    
    miasta = []
    macierze = []

    for i, [miejscowosc, dfi] in enumerate(monthly_avg.groupby("Miejscowość")):
        miasta.append(miejscowosc)
        dane_z_lat = []

        for j, [rok, dfj] in enumerate(dfi.groupby("rok")):
            df_mean = dfj.groupby("miesiąc")["pm25_srednia_miesieczna"].mean()
            # Upewnij się, że mamy wartości dla wszystkich miesięcy
            df_mean = df_mean.reindex(range(1, 13))
            dane_z_lat.append(df_mean.to_numpy())

        macierze.append(np.vstack(dane_z_lat))

    years = [2015, 2018, 2021, 2024]

    # Ustawienia wykresu
    n_cities = len(macierze)
    n_cols = 3  # Liczba kolumn
    n_rows = (n_cities + n_cols - 1) // n_cols  # Oblicz liczbę potrzebnych wierszy 
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 3*n_rows))
    cmap = colormaps["viridis"].copy()
    cmap.set_bad(color="red")

    # Spłaszczanie osi dla pojedynczej miejscowości
    if n_cities == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for idx, (miasto, arr) in enumerate(zip(miasta, macierze)):
        ax = axes[idx]
        sns.heatmap(arr, 
                    ax=ax, 
                    xticklabels=range(1,13), 
                    yticklabels=years,
                    annot=False,
                    cmap=cmap,
                    vmin=0,             
                    vmax=65,           
                    mask=np.isnan(arr),
                    cbar_kws={'shrink': 0.8})
        ax.set_title(miasto, fontsize=10, weight='bold')
        ax.set_xlabel('Miesiąc', fontsize=9)
        ax.set_ylabel('Rok', fontsize=9)
    
    # Schowaj puste osie
    for idx in range(n_cities, len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout()
    plt.show()


def days_over_norm(df):
    """Rysuje wykres słupkowy liczby dni z przekroczeniem normy PM2.5 dla najlepszych i najgorszych stacji."""
    # Zlicz dni powyżej normy dla każdej stacji i roku
    dni_powyzej_normy = (
        df[df['przekroczenie_normy'] == True]
        .drop_duplicates(subset=['kod_stacji', 'Miejscowość', 'rok', 'data_dzien'])
        .groupby(['kod_stacji', 'Miejscowość', 'rok'])
        .size()
        .reset_index(name='dni_powyzej_normy')
    )

    dni_powyzej_normy['rok'] = dni_powyzej_normy['rok'].astype(int)
    
    # Znajdź top 3 i bottom 3 stacje z 2024 roku
    dni_2024 = dni_powyzej_normy[dni_powyzej_normy['rok'] == 2024]
    
    top3 = dni_2024.nlargest(3, 'dni_powyzej_normy')
    bottom3 = dni_2024.nsmallest(3, 'dni_powyzej_normy')
    
    print("Top 3 stacje z największą liczbą dni powyżej normy (2024):")
    print(top3)
    print("\nBottom 3 stacje z najmniejszą liczbą dni powyżej normy (2024):")
    print(bottom3)
    
    # Przygotuj dane do wykresu
    selected_stations = pd.concat([top3, bottom3])
    station_order = selected_stations['kod_stacji'].tolist()
    
    df_plot = dni_powyzej_normy[dni_powyzej_normy['kod_stacji'].isin(station_order)].copy()
    df_plot['label'] = df_plot['kod_stacji'] + ' (' + df_plot['Miejscowość'] + ')'
    label_order = df_plot.drop_duplicates('kod_stacji').set_index('kod_stacji').loc[station_order]['label']
    
    # Rysuj wykres
    plt.figure(figsize=(14, 6))
    sns.barplot(data=df_plot, x='label', y='dni_powyzej_normy', hue='rok', order=label_order)
    plt.xlabel('Stacja (Miejscowość)', weight='bold', fontsize=11)
    plt.ylabel('Dni powyżej normy (>15 μg/m^3)', weight='bold', fontsize=11)
    plt.title('Liczba dni z przekroczeniem normy (15 μg/m^3)', weight='bold', fontsize=14)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
def days_over_norm_by_voivodeship(df, df_metadata):
    """Rysuje wykres słupkowy liczby dni z przekroczeniem normy PM2.5 dla województw."""

    # Przypisz województwa do kodów stacji
    voivodenship_mapping = get_voivodeship_mapping(df_metadata)
    df = df.copy()
    df['Województwo'] = df['kod_stacji'].map(voivodenship_mapping)

    # Czy w danym województwie danego dnia było przekroczenie
    woj_dzien = (
        df.groupby(['Województwo', 'rok', 'data_dzien'])['przekroczenie_normy']
        .any()  # co najmniej jedna stacja
        .reset_index()
    )

    # Zlicz dni z przekroczeniem
    woj_agg = (
        woj_dzien[woj_dzien['przekroczenie_normy']]
        .groupby(['Województwo', 'rok'])
        .size()
        .reset_index(name='dni_powyzej_normy')
    )
    # Rysuj wykres
    plt.figure(figsize=(14, 6))
    sns.barplot(data=woj_agg, x='Województwo', y='dni_powyzej_normy', hue='rok')
    plt.xlabel('Województwo', weight='bold', fontsize=11)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Dni powyżej normy (>15 μg/m^3)', weight='bold', fontsize=11)
    plt.title('Liczba dni z przekroczeniem normy (15 μg/m^3) według województw', weight='bold', fontsize=14)
    plt.legend()
    plt.tight_layout()
    plt.show()