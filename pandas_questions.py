"""Plotting referendum results in pandas.

In short, we want to make a beautiful map to report results of a referendum.
We aim to depict results similarly to maps found here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions, and finally plot them on a map using `geopandas`.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = pd.merge(
        regions,
        departments,
        left_on="code",
        right_on="region_code"
    )
    merged = merged[
        ["region_code", "name_x", "code_y", "name_y"]
    ].rename(
        columns={
            "region_code": "code_reg",
            "name_x": "name_reg",
            "code_y": "code_dep",
            "name_y": "name_dep",
        }
    )
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    Drop the lines relative to DOM-TOM-COM departments and French living
    abroad.
    """
    referendum = referendum[
        ~referendum["Department code"].str.startswith("Z")
    ]
    referendum["Department code"] = referendum["Department code"].apply(
        lambda x: f"0{x}" if len(x) == 1 else x
    )
    merged = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep"
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    results = referendum_and_areas.groupby("code_reg")[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ].sum()

    dict_reg = referendum_and_areas[
        ["code_reg", "name_reg"]
    ].drop_duplicates().set_index("code_reg")["name_reg"].to_dict()

    results["name_reg"] = results.index.map(dict_reg)
    return results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    ref_tot = referendum_result_by_regions[
        ['Choice B', 'Choice A']
        ].sum(axis=1)
    referendum_result_by_regions['ratio'] = referendum_result_by_regions[
        'Choice A']/ref_tot
    geo = gpd.read_file('data/regions.geojson')
    referendum_result_by_regions = gpd.GeoDataFrame(
        pd.merge(
            referendum_result_by_regions,
            geo, left_on='code_reg',
            right_on='code'))
    referendum_result_by_regions.plot(column='ratio')
    return referendum_result_by_regions


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
