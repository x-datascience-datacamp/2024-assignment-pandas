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
    referendum = pd.read_csv("data/referendum.csv",
                             sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame."""
    merged_reg_dep = pd.merge(
        regions, departments,
        left_on='code', right_on='region_code',
        suffixes=('_reg', '_dep')
    )
    merged_reg_dep = merged_reg_dep[
        ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    ]
    return merged_reg_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame."""
    regions_and_departments["code_dep"] = regions_and_departments[
        "code_dep"
    ].str.lstrip('0')
    merged_ref = pd.merge(
        regions_and_departments,
        referendum,
        left_on='code_dep',
        right_on='Department code'
    )
    return merged_ref


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region."""
    merged_ref_areas = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })
    return merged_ref_areas


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum."""
    geodata = gpd.read_file("./data/regions.geojson")
    referendum_result_by_regions["code"] = referendum_result_by_regions.index
    merged = pd.merge(geodata, referendum_result_by_regions)
    all_expressed = merged["Choice A"] + merged["Choice B"]
    merged['ratio'] = merged['Choice A'] / all_expressed
    merged = gpd.GeoDataFrame(merged)
    merged.plot(column="ratio")
    plt.show()
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
