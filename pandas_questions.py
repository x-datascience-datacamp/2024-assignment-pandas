"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.DataFrame(pd.read_csv('data/referendum.csv', sep = ';', header = 0))
    regions = pd.DataFrame(pd.read_csv('data/regions.csv', sep = ',', header = 0))
    departments = pd.DataFrame(pd.read_csv('data/departments.csv', sep = ',', header = 0))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg = regions[['code', 'name']]
    reg = reg.rename(columns = {"code": "code_reg", "name": "name_reg"})
    dep = departments[['code', 'name', 'region_code']]
    dep = dep.rename(columns = {"code": "code_dep", "name": "name_dep", "region_code": "code_reg"})
    result = reg.merge(dep, how = "inner" , on = "code_reg")
    return pd.DataFrame(result)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    
    ref = referendum.rename(columns = {"Department code": "code_dep"})
    ref['code_dep'] = ref['code_dep'].apply(lambda x: f"{int(x):02d}" if str(x).isdigit() and 1 <= int(x) <= 9 else x)

    df = pd.DataFrame(regions_and_departments.merge(ref, how='inner', on='code_dep'))
    
    dep_list = ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion',
       'Mayotte', 'Saint-Pierre-et-Miquelon', 'Saint-Barthélemy',
       'Saint-Martin', 'Terres australes et antarctiques françaises',
       'Wallis et Futuna', 'Polynésie française', 'Nouvelle-Calédonie',
       'Île de Clipperton']
    
    df = df.drop(df[df["name_dep"].isin(dep_list)].index)
    df['Department code'] = df['code_dep']
    return pd.DataFrame(df)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',      
        'Registered': 'sum',      
        'Abstentions': 'sum',     
        'Null': 'sum',           
        'Choice A': 'sum',        
        'Choice B': 'sum'         
    }).reset_index()

    grouped.set_index('code_reg', inplace=True)
    
    return pd.DataFrame(grouped)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file('data/regions.geojson')

    # Calculer le ratio des votes pour Choice A sur les votes exprimés
    referendum_result_by_regions = referendum_result_by_regions.copy()
    referendum_result_by_regions['ratio'] = (
        referendum_result_by_regions['Choice A'] /
        (referendum_result_by_regions['Choice A'] + referendum_result_by_regions['Choice B'])
    )

    # Fusionner les données géographiques avec les résultats
    merged = regions_geo.merge(
        referendum_result_by_regions,
        left_on='code',  # Colonne dans le fichier GeoJSON
        right_index=True  # `code_reg` est l'index de referendum_result_by_regions
    )

    # Tracer la carte avec la méthode GeoDataFrame.plot
    merged.plot(
        column='ratio',  # Colonne utilisée pour colorer la carte
        cmap='coolwarm',  # Palette de couleurs
        legend=True,      # Ajouter une légende
        figsize=(10, 8)   # Taille de la figure
    )
    return gpd.GeoDataFrame(merged)


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
