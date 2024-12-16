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
    referendum: pd.DataFrame = pd.read_csv("data/referendum.csv", sep=";")
    regions: pd.DataFrame = pd.read_csv("data/regions.csv")
    departments: pd.DataFrame = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(
    regions: pd.DataFrame, departments: pd.DataFrame
):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    dep = departments[["region_code", "code", "name"]].copy()
    dep = dep.rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
        }
    )

    reg = regions[["code", "name"]].copy()
    reg = reg.rename(columns={"code": "code_reg", "name": "name_reg"})

    regions_and_departments = dep.merge(reg, how="left", on="code_reg")

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # drop dept codes starting with Z
    ref = referendum[~referendum["Department code"].str.startswith("Z")]
    # add a 0 in front of dept smaller than 10
    ref["Department code"] = ref["Department code"].apply(
        lambda x: f"0{x}" if len(x) == 1 else x
    )

    print(ref["Department code"].unique())
    print(regions_and_departments["code_dep"].unique())
    referendum_and_areas: pd.DataFrame = ref.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="left",
    )

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.fillna(0)
    referendum_result_by_regions: pd.DataFrame = (
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
        .reset_index(drop=False)
    )
    referendum_result_by_regions = referendum_result_by_regions.set_index(
        "code_reg"
    )
    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("data/regions.geojson").drop(columns="nom")

    referendum_results = geo_data.merge(
        referendum_result_by_regions,
        left_on="code",
        right_on="code_reg",
        how="right",
    )
    selected_vote = "Choice A"
    referendum_results["ratio"] = referendum_results[
        selected_vote
    ] / referendum_results[["Choice A", "Choice B"]].sum(axis=1)
    ax = referendum_results.plot(
        column="ratio",
        cmap="Blues",
        legend=True,
        legend_kwds={"label": "Ratio of vote"},
    )
    ax.set_title(f"Ratio of expression of {selected_vote} by region")
    ax.axis("off")
    return referendum_results


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    # print(referendum_and_areas.shape)
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    #  print(referendum_results["Registered"].sum())
    print(referendum_results)

    final_df = plot_referendum_map(referendum_results)

    plt.show()
    # print(final_df)
