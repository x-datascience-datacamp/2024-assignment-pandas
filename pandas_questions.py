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
    regions = pd.read_table("data/regions.csv", sep=",")
    referendum = pd.read_table("data/referendum.csv", sep=";")
    departments = pd.read_table("data/departments.csv", sep=",")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions[["code", "name"]]
    departments = departments[["region_code", "code", "name"]]
    regions.columns = ["region_code", "name"]
    merged = pd.merge(regions, departments, on="region_code")
    merged.columns = ["code_reg", "name_reg", "code_dep", "name_dep"]
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum.loc[
        referendum["Department name"] != "FRANCAIS DE L'ETRANGER"
    ]
    regions_and_departments = regions_and_departments.loc[
        regions_and_departments["code_reg"] != "COM"
    ]
    referendum["Department code"] = referendum["Department code"].apply(
        lambda x: x.zfill(2)
    )

    merged = pd.merge(
        regions_and_departments,
        referendum,
        left_on="code_dep",
        right_on="Department code",
        how="inner",
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas[
        [
            "code_reg",
            "name_reg",
            "Registered",
            "Abstentions",
            "Null",
            "Choice A",
            "Choice B",
        ]
    ]
    return (
        referendum_and_areas.set_index("code_reg")
        .groupby(by=["name_reg"])
        .sum()
        .reset_index()
    )


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    data = gpd.read_file("./data/regions.geojson")
    merged = gpd.GeoDataFrame(
        pd.merge(data, referendum_result_by_regions, left_on="nom", right_on="name_reg")
    )
    merged["ratio"] = merged["Choice A"] / (merged["Choice B"] + merged["Choice A"])
    merged.plot(column="ratio", legend=True)

    return merged


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
