"""Plotting referendum results in pandas.

In short, we want to make a beautiful map to report results of a referendum.
We want something similar to the maps here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as a pandas.DataFrame, merge the info and
aggregate them by regions, and finally plot them on a map using `geopandas`.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    combined = pd.merge(
        regions,
        departments,
        how="inner",
        left_on="code",
        right_on="region_code",
        suffixes=["_reg", "_dep"]
    )
    combined = combined[["code_reg", "name_reg", "code_dep", "name_dep"]]
    return combined


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum data with regions_and_departments."""
    referendum["Department code"] = (
        referendum["Department code"].astype(str).str.zfill(2)
    )
    combined_ref = pd.merge(
        referendum,
        regions_and_departments,
        how="inner",
        left_on="Department code",
        right_on="code_dep"
    )
    return combined_ref


def compute_referendum_result_by_regions(referendum_and_areas):
    """Compute results by region.

    The returned DataFrame should have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    indexed by 'code_reg'.
    """
    referendum_and_areas = referendum_and_areas[
        ["code_reg", "name_reg", "Registered", "Abstentions",
         "Null", "Choice A", "Choice B"]
    ]
    results_by_reg = referendum_and_areas.groupby("code_reg").agg({
        "name_reg": "first",
        "Registered": "sum",
        "Abstentions": "sum",
        "Null": "sum",
        "Choice A": "sum",
        "Choice B": "sum"
    })
    return results_by_reg


def plot_referendum_map(referendum_result_by_regions):
    """Plot the referendum map showing the ratio of Choice A."""
    geo = gpd.read_file("data/regions.geojson")
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"]
        / (referendum_result_by_regions["Choice A"]
           + referendum_result_by_regions["Choice B"])
    )
    geo_data = pd.merge(
        geo,
        referendum_result_by_regions,
        how="inner",
        left_on="code",
        right_on="code_reg"
    )
    geo_data.plot(column="ratio", legend=True)
    return geo_data


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
