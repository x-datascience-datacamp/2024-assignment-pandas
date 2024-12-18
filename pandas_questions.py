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
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
        # Renommer les colonnes pour clarification avant fusion
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(columns={"code": "code_dep", "name": "name_dep", "region_code": "code_reg"})

    # Fusion des DataFrames sur le code de région
    merged = pd.merge(departments, regions, on="code_reg", how="inner")

    # Sélection des colonnes dans l'ordre souhaité
    merged = merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """
    Merge referendum and regions_and_departments in one DataFrame.

    Args:
        referendum (pd.DataFrame): The referendum data.
        regions_and_departments (pd.DataFrame): The merged regions and departments data.

    Returns:
        pd.DataFrame: A DataFrame containing referendum data merged with region and department data,
                      excluding lines related to DOM-TOM-COM and French living abroad.
    """
    # Exclure les départements DOM-TOM-COM et les Français de l'étranger
    # DOM-TOM-COM : codes départements qui commencent par 97 ou 98.
    # Français vivant à l'étranger : code département 99.
    areas_to_exclude = ['97', '98', '99']
    filtered_areas = regions_and_departments[
        ~regions_and_departments['code_dep'].str.startswith(tuple(areas_to_exclude))
    ]

    # Renommer la colonne dans referendum pour alignement avant la fusion
    referendum = referendum.rename(columns={"DepartmentCode": "code_dep"})

    # Fusion des DataFrames sur la colonne 'code_dep'
    merged = pd.merge(referendum, filtered_areas, on="code_dep", how="inner")

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Grouper par région (code_reg) et sommer les colonnes pertinentes
    grouped = referendum_and_areas.groupby(['code_reg', 'name_reg']).sum()

    # Garder uniquement les colonnes pertinentes
    result = grouped[['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].reset_index()

    # Réindexer par code_reg
    result = result.set_index('code_reg')

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Charger les données géographiques
    regions_geo = gpd.read_file("regions.geojson")

    # Calculer le ratio 'Choice A' / votes exprimés
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"] / 
        (referendum_result_by_regions["Choice A"] + referendum_result_by_regions["Choice B"])
    )

    # Fusionner les données géographiques avec les résultats du référendum
    regions_geo = regions_geo.rename(columns={"code": "code_reg"})
    regions_geo["code_reg"] = regions_geo["code_reg"].astype(int)  # Harmoniser les types de données
    merged_geo = regions_geo.merge(referendum_result_by_regions, on="code_reg", how="left")

    # Tracer la carte
    ax = merged_geo.plot(
        column="ratio",  # Colonne utilisée pour la coloration
        cmap="Blues",    # Palette de couleurs
        legend=True,     # Afficher la légende
        legend_kwds={"label": "Ratio of Choice A"},  # Libellé de la légende
        figsize=(10, 8)  # Taille de la figure
    )
    plt.title("Referendum Results by Region")
    plt.show()

    return merged_geo


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
