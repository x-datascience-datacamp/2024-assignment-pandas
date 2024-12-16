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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = pd.merge(regions, departments, left_on='code',
                      right_on='region_code', suffixes=('_reg', '_dep'))

    return merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    merged = pd.merge(referendum, regions_and_departments,
                      left_on='Department code',
                      right_on='code_dep')

    merged = merged[(merged['code_reg'] != 'COM') &
                    (merged['code_reg'] != '01') &
                    (merged['code_reg'] != '02') &
                    (merged['code_reg'] != '03') &
                    (merged['code_reg'] != '04') &
                    (merged['code_reg'] != '05') &
                    (merged['code_reg'] != '06')]
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    count_by_regions = referendum_and_areas\
        .groupby(['code_reg', 'name_reg']).sum()

    count_by_regions.reset_index(inplace=True)
    count_by_regions.index = count_by_regions['code_reg']

    return count_by_regions[['name_reg', 'Registered',
                             'Abstentions', 'Null', 'Choice A', 'Choice B']]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file(r"data\regions.geojson")
    merged = pd.merge(gdf, referendum_result_by_regions,
                      left_on='code', right_on='code_reg')
    merged['ratio'] = merged['Choice A'] /\
        (merged['Choice A'] + merged['Choice B'])
    merged.plot(column='ratio', legend=True, cmap='YlOrRd')

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
