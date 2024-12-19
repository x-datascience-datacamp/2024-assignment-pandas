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
    """Load data from the CSV files referendum/regions/departments."""
    referendum_file = pd.read_csv("data/referendum.csv", delimiter=";")
    regions_file = pd.read_csv("data/regions.csv")
    departments_file = pd.read_csv("data/departments.csv")

    referendum = pd.DataFrame(referendum_file)
    regions = pd.DataFrame(regions_file)
    departments = pd.DataFrame(departments_file)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    left = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    right = departments.rename(
        columns={
            "code": "code_dep",
            "name": "name_dep",
            "region_code": "code_reg",
        }
    )
    return pd.merge(left=left, right=right, on="code_reg", how="left")[
        ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum["code_dep"] = referendum["Department code"]
    regions_and_departments["code_dep"] = regions_and_departments[
        "code_dep"
    ].str.lstrip("0")
    return pd.merge(
        left=referendum,
        right=regions_and_departments,
        on="code_dep",
        how="inner",
    )


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas[
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
    df = df.groupby(["code_reg", "name_reg"]).sum()
    df.reset_index(inplace=True)
    df.set_index("code_reg", inplace=True)
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
    should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file("data/regions.geojson")

    referendum_result_by_regions["Total expressed"] = (
        referendum_result_by_regions["Registered"]
        - referendum_result_by_regions["Abstentions"]
        - referendum_result_by_regions["Null"]
    )

    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"]
        / referendum_result_by_regions["Total expressed"]
    )
    merged_data = pd.merge(
        regions_geo,
        referendum_result_by_regions,
        left_on="nom",
        right_on="name_reg",
    )
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    merged_data.plot(column="ratio", cmap="coolwarm", legend=True, ax=ax)
    ax.set_title(
        "Referendum Results: Rate of 'Choice A' Over Expressed Ballots"
    )
    plt.axis("off")

    return merged_data


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
