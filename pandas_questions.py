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
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={"code" : "code_reg", "name" : "name_reg"})
    regions = regions[["code_reg","name_reg"]]
    departments = departments.rename(columns={"region_code" : "code_reg", "code" : "code_dep", "name" : "name_dep"})
    departments = departments[["code_reg", "code_dep", "name_dep"]]
    reg_and_dep = pd.merge(departments, regions, how = "inner", on = "code_reg")
    return reg_and_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments['code_dep'] = regions_and_departments['code_dep'].str.lstrip('0')
    merged_df = pd.merge(referendum, regions_and_departments,
                         left_on='Department code', right_on='code_dep')
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result_by_regions = referendum_and_areas[['code_reg', 
                                              'name_reg', 
                                              'Registered', 
                                              'Abstentions',
                                              'Null', 
                                              'Choice A', 
                                              'Choice B']]
    result_by_regions = result_by_regions.groupby(by=['code_reg', 'name_reg']).sum()
    result_by_regions.reset_index('name_reg', inplace = True)
    return result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file('data/regions.geojson')
    regions_geo = regions_geo.rename(columns = {'code': 'code_reg'})
    ref = pd.merge(ref, regions_geo, how='inner', on='code_reg')
    voted = (ref['Choice A'] + ref['Choice B'])
    ref['ratio'] = ref['Choice A'] / voted
    merged_gpd = gpd.GeoDataFrame(ref)
    merged_gpd.plot(column='ratio', legend=True)
    return merged_gpd


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
