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
    """
    Load dataset.

    Output
    """
    referendum = pd.read_csv('data/referendum.csv', sep=";")
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={
        'code': 'code_reg',
        'name': 'name_reg'
    })
    departments = departments.rename(columns={
        'region_code': 'code_reg',
        'name': 'name_dep',
        'code': 'code_dep'
    })
    regions_and_departments = pd.merge(
        regions, departments, on='code_reg', how='left'
    )
    regions_and_departments = regions_and_departments[[
        'code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['code_dep'] = referendum['Department code']
    referendum['name_dep'] = referendum['Department name']
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].str.lstrip('0')
        )
    referendum = referendum[referendum['code_dep'].str[0] != 'Z']
    referendum_and_areas = pd.merge(
        referendum, regions_and_departments, on='code_dep', how='inner'
        )
    referendum_and_areas = referendum_and_areas.rename(columns={
        'name_dep_x': 'name_dep'
    })
    referendum_and_areas = referendum_and_areas[[
        'Department code', 'Department name', 'Town code',
        'Town name', 'Registered', 'Abstentions', 'Null',
        'Choice A', 'Choice B', 'code_dep', 'code_reg', 'name_reg', 'name_dep'
        ]]
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas[[
        'code_reg', 'name_reg', 'Registered', 'Abstentions',
        'Null', 'Choice A', 'Choice B'
        ]]
    referendum_results = referendum_and_areas.groupby([
        'code_reg', 'name_reg'
        ]).sum()
    referendum_results = referendum_results.reset_index()
    referendum_results = referendum_results.set_index('code_reg')
    return referendum_results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geojson = gpd.read_file("data/regions.geojson")
    geo = geojson[['geometry']]
    geo['code_reg'] = geojson['code']
    geo = geo.set_index('code_reg')
    geo = referendum_result_by_regions.join(geo)
    geo = gpd.GeoDataFrame(geo)
    geo['ratio'] = geo['Choice A'] / (geo['Choice A']+geo['Choice B'])
    geo.plot('ratio')
    return geo


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
    plot_referendum_map(referendum_results)
    plt.show()
