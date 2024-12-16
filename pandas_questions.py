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
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    dep = departments[["region_code", "code", "name"]]
    dep.columns = ["code_reg", "code_dep", "name_dep"]
    reg = regions[["code", "name"]]
    reg.columns = ["code_reg", "name_reg"]

    merged = pd.merge(reg, dep, on="code_reg", how="left")
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Dropping all the DOM-TOM-Departements

    referendum["code_dep"] = referendum["Department code"].str.zfill(2)
    merged = pd.merge(
        referendum, regions_and_departments, on="code_dep", how="left"
    ).dropna()

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped_ref_areas = (
        referendum_and_areas[
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
        .groupby(["code_reg", "name_reg"])
        .sum()
    )
    grouped_ref_areas = grouped_ref_areas.reset_index().set_index("code_reg")

    return grouped_ref_areas


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_df = gpd.read_file("data/regions.geojson")
    referendum_result_by_regions["ratio"] = referendum_result_by_regions[
        "Choice A"
    ] / referendum_result_by_regions[["Choice A", "Choice B"]].sum(axis=1)
    referendum_result_by_regions = gpd.GeoDataFrame(
        pd.merge(
            referendum_result_by_regions.reset_index(),
            geo_df,
            left_on="code_reg",
            right_on="code",
        )
    )
    referendum_result_by_regions.plot(column="Choice A", legend=True)

    return referendum_result_by_regions


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    reg_and_dep = merge_regions_and_departments(df_reg, df_dep)
    refer_and_areas = merge_referendum_and_areas(referendum, reg_and_dep)
    referendum_results = compute_referendum_result_by_regions(refer_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
