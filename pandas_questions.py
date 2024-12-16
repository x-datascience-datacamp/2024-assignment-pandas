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
    referendum = pd.read_csv("data/referendum.csv", sep=";", header=0)
    regions = pd.read_csv("data/regions.csv", sep=";", header=0)
    departments = pd.read_csv("data/departments.csv", sep=";", header=0)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={'code': 'code_reg'})
    departments = departments.rename(columns={'region_code': 'code_reg'})
    merged_df = pd.merge(regions, departments, on='code_reg')

    # Rename columns for clarity
    merged_df = merged_df.rename(
        columns={'name_x': 'name_reg',
                 'code': 'code_dep',
                 'name_y': 'name_dep'})

    return merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    referendum = referendum.rename(columns={'Department code': 'code_dep', 'Department name': 'name_dep'})
    merged_df1 = pd.merge(referendum, regions_and_departments, on='code_dep')
    dom_tom_com_list = [
        'ZA', 'ZB', 'ZC', 'ZD',
        'ZM', 'ZN', 'ZP', 'ZS',
        'ZW', 'ZX', 'ZZ'
    ]
    merged_df1 = merged_df1.drop(merged_df1[merged_df1['code_dep'].isin(dom_tom_com_list)].index)
    merged_df1 = merged_df1.drop(merged_df1[merged_df1['name_dep'].str.contains('FRANCAIS DE L\'ETRANGER')].index)

    return merged_df1

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby(['code_reg', 'name_reg'], as_index=True).sum()[
        ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    df.reset_index(inplace=True)
    df.set_index('code_reg', inplace=True)

    return referendum_and_areas['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file("data//regions.geojson")
    referendum_geo = referendum_result_by_regions.merge(
        regions_geo,
        left_on="code_reg",
        right_on="code"
    )
    referendum_geo = gpd.GeoDataFrame(data=referendum_geo)
    referendum_geo["ratio"] = (
            referendum_geo["Choice A"] / (referendum_geo[
                                "Choice A"
                            ] + referendum_geo["Choice B"]))
    referendum_geo.plot("ratio")
    return referendum_geo


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
