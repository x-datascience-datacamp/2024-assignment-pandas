"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using geopandas.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

#Second test
def load_data():
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    merged = pd.merge(
        departments, regions,
        left_on="region_code", right_on="code",
        suffixes=("_dep", "_reg"), how='left'
    )
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    referendum = referendum[referendum["Department code"].str.isnumeric()]
    merged = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how='left'
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    grouped = referendum_and_areas.groupby("code_reg").agg({
        "name_reg": "first",
        "Registered": "sum",
        "Abstentions": "sum",
        "Null": "sum",
        "Choice A": "sum",
        "Choice B": "sum",
    })
    return grouped


def plot_referendum_map(referendum_result_by_regions):
    geo_data = gpd.read_file("data/regions.geojson")
    merged = geo_data.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True,
        how='left'
    )
    merged["ratio"] = merged["Choice A"] / (
        merged["Choice A"] + merged["Choice B"]
    )
    ax = merged.plot(column="ratio", cmap="RdYlGn", legend=True)
    legend = ax.get_legend()
    legend.set_title("Choice A Ratio")
    return merged


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)
    plot_referendum_map(referendum_results)
    plt.show()
