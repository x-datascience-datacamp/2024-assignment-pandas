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

    merged = pd.merge(departments, regions, left_on='region_code', right_on='code', suffixes=('_dep', '_reg'))
    regions_and_departments = merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']].rename(columns={
        'code_reg': 'code_reg', 
        'name_reg': 'name_reg',
        'code_dep': 'code_dep',
        'name_dep': 'name_dep'
    })

    for i in range(1, 10):
        regions_and_departments['code_dep'] = regions_and_departments['code_dep'].str.replace(f"0{i}", f"{i}")

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum_and_areas = pd.merge(referendum, regions_and_departments,
                                    left_on='Department code',
                                    right_on='code_dep')

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    referendum_result_by_regions = referendum_and_areas.groupby(['code_reg', 'name_reg']).agg(
        Registered=('Registered', 'sum'),
        Abstentions=('Abstentions', 'sum'),
        Null=('Null', 'sum'),
        Choice_A=('Choice A', 'sum'),
        Choice_B=('Choice B', 'sum')
        ).reset_index()
    
    referendum_result_by_regions = referendum_result_by_regions.rename(columns={'Choice_A': 'Choice A', 'Choice_B': 'Choice B'})

    # Setting 'code_reg' as the index
    referendum_result_by_regions = referendum_result_by_regions.set_index('code_reg')

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_data = gpd.read_file('data/regions.geojson')
    geo_data = geo_data.merge(referendum_result_by_regions, left_on='nom', right_on='name_reg')
    geo_data = geo_data.rename(columns={'Choice_A': 'Choice A', 'Choice_B': 'Choice B'})

    geo_data['ratio'] = geo_data['Choice A'] / (geo_data['Choice A'] + geo_data['Choice B'])
    geo_data.plot(column='ratio', legend=True, cmap='coolwarm')

    return geo_data



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