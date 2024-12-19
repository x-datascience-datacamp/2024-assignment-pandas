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
    referendum = pd.read_csv("data/referendum.csv", delimiter=';')
    regions = pd.read_csv("data/regions.csv", delimiter=',')
    departments = pd.read_csv("data/departments.csv", delimiter=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = pd.merge(
        departments,
        regions,
        left_on='region_code',  
        right_on='code',       
        suffixes=('_dep', '_reg')
    )

    merged = merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return merged

def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    # Standardize Department code format: Add leading zeros
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    # Debug unmatched codes after fixing leading zeros
    unmatched_codes = set(referendum['Department code']) - set(regions_and_departments['code_dep'])
    referendum = referendum[~referendum['Department code'].isin(unmatched_codes)]
    merged = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner"
    )
    excluded_region_codes = ['971', '972', '973', '974', '975', '976', '977', '978', '99']
    merged = merged[~merged['code_reg'].isin(excluded_region_codes)]
    return merged

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby(['code_reg', 'name_reg']).sum()
    grouped = grouped.reset_index()
    result = grouped[['code_reg', 'name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    return result.set_index('code_reg')


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo = gpd.read_file("data/regions.geojson")
    merged = geo.merge(referendum_result_by_regions, left_on='code', right_on='code_reg')
    merged['ratio'] = merged['Choice A'] / (merged['Choice A'] + merged['Choice B'])
    
    merged.plot(column='ratio', legend=True, cmap='coolwarm')
    plt.title("Referendum Results: Choice A Ratio")
    plt.axis("off")
    
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
