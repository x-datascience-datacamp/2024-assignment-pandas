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
    # print(referendum.shape)
    # print(regions.shape)
    # print(departments.shape)

    # print(referendum.head())
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(regions, departments, left_on="code", right_on="region_code")
    # print(df.columns)
    df = df[["code_x", "name_x", "code_y", "name_y"]]
    df.columns = ["code_reg", "name_reg", "code_dep", "name_dep"]
    # print(df.head())
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # adda 0 to single digit department code to the left
    referendum["Department code"] = (
        referendum["Department code"].astype(str).str.zfill(2)
    )
    df = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
    )

    df = df[df["code_reg"] != "COM"]
    # drop all lines with region code from 01 to 06
    df = df[~df["code_reg"].str.contains("0[1-6]")]

    print(df.shape)

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # print(referendum_and_areas.columns)
    df = referendum_and_areas.groupby("code_reg")[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ].sum()
    df = pd.concat(
        [referendum_and_areas.groupby("code_reg")["name_reg"].first(), df],
        axis=1,
    )
    # assert the column names
    assert df.columns.tolist() == [
        "name_reg",
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B",
    ]
    # assert index is code_reg
    assert df.index.name == "code_reg"
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("data/regions.geojson")
    gdf = gdf.merge(
        referendum_result_by_regions, left_on="code", right_index=True
    )
    gdf["ratio"] = gdf["Choice A"] / (gdf["Choice A"] + gdf["Choice B"])

    gdf.plot(column="ratio", legend=True)

    return gdf


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
