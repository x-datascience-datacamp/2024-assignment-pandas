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


def load_data() -> pd.DataFrame:
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv", sep=",")
    departments = pd.read_csv("./data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(
    regions: pd.DataFrame, departments: pd.DataFrame
) -> pd.DataFrame:
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    return (
        regions[["code", "name"]]
        .merge(
            departments[["region_code", "code", "name"]],
            left_on="code",
            right_on="region_code",
            how="inner",
            suffixes=["_reg", "_dep"],
        )
        .drop(labels="region_code", axis=1)
    )


def merge_referendum_and_areas(
    referendum: pd.DataFrame, regions_and_departments: pd.DataFrame
) -> pd.DataFrame:
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abrroad.
    """
    referendum["Department code"] = (
        referendum["Department code"].astype(str).str.zfill(2)
    )
    return referendum.merge(
        regions_and_departments[
            ~regions_and_departments["code_reg"].isin(["DOM", "TOM", "COM"])
        ],
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )


def compute_referendum_result_by_regions(
    referendum_and_areas: pd.DataFrame,
) -> pd.DataFrame:
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    return (
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
        .groupby(by=["code_reg", "name_reg"])
        .sum()
        .reset_index(level="name_reg")
    )


def plot_referendum_map(referendum_result_by_regions: pd.DataFrame):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("./data/regions.geojson")
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"]
        / (
            referendum_result_by_regions["Choice A"]
            + referendum_result_by_regions["Choice B"]
        )
    )
    res_geo = geo_data.merge(
        referendum_result_by_regions, left_on="code", right_index=True
    )
    res_geo = gpd.GeoDataFrame(res_geo, geometry="geometry")
    res_geo.plot(
        column="ratio",
        legend=True,
        legend_kwds={"label": "Choice A ratio"},
        cmap="OrRd",
    )
    return res_geo


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    ref_results = compute_referendum_result_by_regions(referendum_and_areas)
    print(ref_results)

    plot_referendum_map(ref_results)
    plt.show()
