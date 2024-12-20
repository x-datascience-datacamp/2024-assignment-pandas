"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:`
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    region_temp = regions.drop(columns=["id", "slug"]).rename(
        columns={"code": "code_reg", "name": "name_reg"}
    )
    dept_temp = departments.drop(columns=["id", "slug"]).rename(
        columns={"code": "code_dep", "name": "name_dep", "region_code": "code_reg"}
    )
    df = pd.merge(region_temp, dept_temp, on="code_reg", how="left")

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    regions_and_departments = regions_and_departments[
        ~(regions_and_departments["code_reg"] == "COM")
    ]
    referendum.loc[referendum["Department code"].str.len() == 1, "Department code"] = (
        referendum["Department code"].str.zfill(2)
    )
    referendum = referendum[~referendum["Department code"].str.match("^[Z]")]
    # quit()

    df = pd.merge(
        regions_and_departments,
        referendum,
        left_on="code_dep",
        right_on="Department code",
        how="right",
    )

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.set_index("code_reg")
    referendum_and_areas[
        ["Registered", "Abstentions", "Choice A", "Choice B", "Null"]
    ] = referendum_and_areas[
        ["Registered", "Abstentions", "Choice A", "Choice B", "Null"]
    ].astype(
        int
    )
    referendum_result = (
        referendum_and_areas[
            ["name_reg", "Registered", "Abstentions", "Choice A", "Choice B", "Null"]
        ]
        .groupby(["code_reg", "name_reg"])
        .sum()
    )
    referendum_result = referendum_result.reset_index().set_index("code_reg")
    return referendum_result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `=`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_df = gpd.read_file("data/regions.geojson")
    merged_df = geo_df.merge(
        referendum_result_by_regions, how="inner", left_on="code", right_on="code_reg"
    )
    merged_df["ratio"] = merged_df["Choice A"] / (
        merged_df["Choice A"] + merged_df["Choice B"]
    )

    merged_df.plot(column="ratio", legend=True)
    plt.title("Referendum Results: Choice A Ratio by Region")
    plt.show()
    return merged_df


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
