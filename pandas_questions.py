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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # rename columns for the final dataframe
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    departments = departments.rename(columns={'region_code': 'code_reg',
                                              'code': 'code_dep',
                                              'name': 'name_dep'})

    # merge regions and departments in one dataframe
    regions_and_departments = departments.merge(regions,
                                                on='code_reg',
                                                how='left')

    # keep specific columns
    regions_and_departments = regions_and_departments[
        ['code_reg', 'name_reg', 'code_dep', 'name_dep']
        ]

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # replace numbers to have 2 digits in 'Department code'
    referendum['Department code'] = referendum['Department code'].str.zfill(2)

    # remove DOM-TOM-COM and French people living abroad
    regions_and_departments = regions_and_departments[
        regions_and_departments['code_reg'] != 'COM']
    regions_and_departments = regions_and_departments[
        ~regions_and_departments['code_dep'].str.startswith('97')]
    referendum = referendum[~referendum['Department code'].str.startswith('Z')]

    # merge referendum and areas in one dataframe
    referendum_and_areas = referendum.merge(regions_and_departments,
                                            left_on='Department code',
                                            right_on='code_dep',
                                            how='left')

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # group and index by code_reg
    region_grp = referendum_and_areas.groupby(['code_reg', 'name_reg']).sum()[
        ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
        ]

    # keep specific columns
    compute_referendum_result_by_regions = region_grp.reset_index()
    compute_referendum_result_by_regions.set_index('code_reg', inplace=True)

    return compute_referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # load geographic data
    geographic_data = gpd.read_file('data/regions.geojson')

    # merge the info
    geographic_data = geographic_data.merge(referendum_result_by_regions,
                                            left_on='code',
                                            right_on='code_reg',
                                            how='left')

    # compute the ratio (rate of Choice A over all expressed ballots)
    temp = geographic_data['Choice A'] + geographic_data['Choice B']
    geographic_data['ratio'] = geographic_data['Choice A'] / temp

    # display the map
    figure, axis = plt.subplots(1, 1, figsize=(10, 8))
    geographic_data.plot(column='ratio', ax=axis, legend=True)
    plt.title("Rate of 'Choice A' by region")

    return geographic_data


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
