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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.
    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.rename(columns={"code": "code_reg", "name": "name_reg"},
                   inplace=True)
    departments.rename(columns={"region_code": "code_reg", "code": "code_dep",
                                "name": "name_dep"}, inplace=True)
    merged = pd.merge(regions, departments, on="code_reg")
    merged.drop(columns={"id_x", "slug_x", "id_y", "slug_y"}, inplace=True)

    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # print(referendum)
    # referendum.rename(columns={"Department code": "code_dep"}, inplace=True)
    referendum["Department code"] = referendum["Department code"].str.zfill(2)
    merged_ref = pd.merge(referendum, regions_and_departments, how="inner",
                          left_on="Department code", right_on="code_dep")
    # missing_codes = referendum[~referendum["code_dep"].isin
    # (regions_and_departments["code_dep"])]
    #   print("Valeurs manquantes", missing_codes["code_dep"].unique())

    values_to_remove = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN', 'ZP', 'ZS', 'ZW',
                        'ZX', 'ZZ']
    filtered_merged_ref = merged_ref[~merged_ref["code_dep"].
                                     isin(values_to_remove)]
    # referendum.rename(columns={"code_dep": "Department code"}, inplace=True)

    # 36565 ligns 95;VAL D'OISE;690;Wy-dit-Joli-Village;279;30;1;83;165
    return pd.DataFrame(filtered_merged_ref)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    aggregated = referendum_and_areas.groupby(['code_reg', 'name_reg'],
                                              as_index=False).sum()
    aggregated = aggregated[['code_reg', 'name_reg', 'Registered',
                             'Abstentions', 'Null', 'Choice A', 'Choice B']]

    aggregated.set_index('code_reg', inplace=True)
    return aggregated


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("data/regions.geojson")

    print("Colonnes du GeoDataFrame (gdf) :", gdf.columns)

    # Calculer le ratio pour chaque région
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"] /
        (referendum_result_by_regions["Choice A"] +
         referendum_result_by_regions["Choice B"])
    )

    print("Colonnes après ajout de 'ratio' :",
          referendum_result_by_regions.columns)
    print("Exemple de ratios :", referendum_result_by_regions["ratio"].head())

    merged_gdf = gdf.merge(referendum_result_by_regions, how="left",
                           left_on="code", right_index=True)
    # print("Colonnes après fusion :", merged_gdf.columns)

    # Vérifier si "ratio" est bien présent
    if "ratio" not in merged_gdf.columns:
        # print("La fusion a échoué à inclure 'ratio'.
        # Vérifiez les clés de fusion.")
        # print("Clés dans gdf['code'] :", gdf["code"].unique())
        # print("Index de referendum_result_by_regions :",
        # referendum_result_by_regions.index.unique())
        raise ValueError("'ratio' pas ajoutée au GeoDataFrame.")

    # Tracer la carte des ratios
    merged_gdf.plot(column="ratio", legend=True, cmap="coolwarm")
    plt.title("Référendum : Ratio de votes pour le 'Choix A' par région")
    plt.axis("off")
    plt.show()

    # Retourner le GeoDataFrame fusionné avec les ratios
    return merged_gdf


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    # print(regions_and_departments)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    print(referendum_and_areas.columns)
    print(referendum_and_areas)

    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
    # End of the file
