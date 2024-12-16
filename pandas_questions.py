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

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(
        regions,
        departments,
        left_on="code",
        right_on="region_code",
        how="left"
    ).rename(
        columns={
            "code_x": "code_reg",
            "name_x": "name_reg",
            "code_y": "code_dep",
            "name_y": "name_dep",
        }
    )[
        ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]
    return merged_df


def process_0_starting_codes(code_dep):
    """
    Remove starting '0' in department codes

    '01' -> '1'
    """
    if code_dep[0] == "0":
        return code_dep[1]
    else:
        return code_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].apply(
            process_0_starting_codes
        )
    )

    merged_df = pd.merge(
        referendum[
            ~referendum["Department code"].str.startswith("Z")
        ],  # DOM-TOM-COM and abroad starts w/ Z
        regions_and_departments[regions_and_departments["code_reg"] != "COM"],
        left_on="Department code",
        right_on="code_dep",
        how="left",
    )

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped_df = (
        referendum_and_areas.groupby(["code_reg", "name_reg"])[
            ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
        ]
        .sum()
        .reset_index("name_reg")
    )

    return grouped_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    regions_map = gpd.read_file("data/regions.geojson")

    merged_df = pd.merge(
        referendum_result_by_regions,
        regions_map,
        left_on=["code_reg", "name_reg"],
        right_on=["code", "nom"],
    ).set_index("code")

    # Registered = Abstentions + Null + Choice A + Choice B
    merged_df["ratio"] = merged_df["Choice A"] / (
        merged_df["Choice A"] + merged_df["Choice B"]
    )

    # DataFrame to GeoDataFrame
    merged_df = gpd.GeoDataFrame(merged_df)
    merged_df.plot(
        column="ratio",
        legend=True,
        cmap="coolwarm",
    )

    plt.axis("off")
    for idx, row in merged_df.iterrows():
        plt.text(
            row.geometry.centroid.x,
            row.geometry.centroid.y,
            f"{row['nom']}",
            fontsize=6,
            ha="center",
        )
    plt.title("Ratio of Choice A to Registered")

    return merged_df


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
        )

    print(plot_referendum_map(referendum_results).head())
    plt.show()
