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
    regions = regions.drop(columns=["id", "slug"])
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.drop(columns=["id", "slug"])
    departments = departments.rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
        }
    )
    df = pd.merge(departments, regions, on="code_reg", how="left")

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    def format_dep_name(dep_name):
        if dep_name[0] == "0":
            return dep_name[1]
        return dep_name

    regions_and_departments["Department code"] = regions_and_departments[
        "code_dep"
    ].apply(format_dep_name)
    referendum = referendum[~referendum["Department code"].str.startswith("Z")]

    df_referendum_and_areas = pd.merge(
        referendum, regions_and_departments, on="Department code", how="left"
    )

    return df_referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    df_grouped = (
        referendum_and_areas.groupby(["code_reg", "name_reg"])[
            ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
        ]
        .sum()
        .reset_index("name_reg")
    )

    return df_grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_df = gpd.read_file("data/regions.geojson")
    geo_df = geo_df.drop(columns=["nom"])
    geo_df = geo_df.rename(columns={"code": "code_reg"})
    referendum_result_by_regions = pd.merge(
        referendum_result_by_regions, geo_df, on="code_reg", how="left"
    )

    referendum_result_by_regions["ratio"] = referendum_result_by_regions[
        "Choice A"
    ] / (
        referendum_result_by_regions["Choice A"]
        + referendum_result_by_regions["Choice B"]
    )

    geo_df_final = gpd.GeoDataFrame(referendum_result_by_regions)
    geo_df_final.plot("ratio", cmap="viridis", legend=True)

    return geo_df_final


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
