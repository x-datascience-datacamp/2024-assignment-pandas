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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_merge = regions[['code', 'name']]
    departments_merge = departments[['region_code', 'code', 'name']]

    regions_merge = regions_merge.rename(columns={'code': 'code_reg',
                                                  'name': 'name_reg'})
    departments_merge = departments_merge.rename(
        columns={'region_code': 'code_reg',
                 'code': 'code_dep', 'name': 'name_dep'})
    regions_and_departments = pd.merge(
        regions_merge, departments_merge, on='code_reg', how='left')

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    
    You can drop the lines relative to DOM-TOM-COM departments,
    and the French living abroad.
    """
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].str.lstrip('0')
    )
    referendum = referendum[referendum['Department code'].str[0] != 'Z']
    referendum_and_areas = referendum.merge(
        regions_and_departments, how='inner', left_on='Department code',
        right_on='code_dep')

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    count_referendum_regions = referendum_and_areas[['name_reg',
                                                     'Registered',
                                                     'Abstentions',
                                                     'Null', 'Choice A',
                                                     'Choice B', 'code_reg']]
    return count_referendum_regions.groupby('code_reg').agg({
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum',
        'name_reg': 'first'
    })


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map.
    * The results should display the rate of 'Choice A' over all
    expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file('data/regions.geojson')

    referendum_result_by_regions['ratio'] = (
        referendum_result_by_regions['Choice A'] /
        (referendum_result_by_regions['Choice A'] +
         referendum_result_by_regions['Choice B'])
    )

    regions_ratio = regions_geo.merge(
        referendum_result_by_regions, how='inner', left_on='nom',
        right_on='name_reg')

    regions_ratio.plot(column='ratio')

    return regions_ratio


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()

    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments)
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas)

    print(referendum_results)

    plot_referendum_map(referendum_results)

    plt.show()
