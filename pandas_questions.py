"""
This module contains functions to load referendum data, merge it with region
and department information, compute referendum results by region, and plot
the results on a map using GeoPandas.
"""


import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    # Load the data into pandas DataFrames
    referendum = pd.read_csv('data/referendum.csv')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Merge the regions and departments data on the 'code_reg' column
    merged = pd.merge(regions, departments, on='code_reg')
    return merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Merge referendum data with regions
    #  and departments data on the 'code_dep' column
    merged = pd.merge(referendum, regions_and_departments, on='code_dep')

    # Drop the rows that correspond
    # to DOM-TOM-COM departments or French living abroad
    merged = merged[~merged['code_dep'].str.startswith('DOM')]
    # Example condition
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Aggregate the data by region using groupby
    referendum_results = referendum_and_areas.groupby('code_reg').agg(
        name_reg=('name_reg', 'first'),
        Registered=('Registered', 'sum'),
        Abstentions=('Abstentions', 'sum'),
        Null=('Null', 'sum'),
        Choice_A=('Choice A', 'sum'),
        Choice_B=('Choice B', 'sum')
    ).reset_index()
    return referendum_results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geographic data with geopandas (geojson format)
    regions = gpd.read_file('data/regions.geojson')

    # Merge the referendum results with the geographic data on 'code_reg'
    merged = pd.merge(
        regions, referendum_result_by_regions,
        left_on='code', right_on='code_reg')

    # Calculate the ratio of 'Choice A' over all expressed ballots
    merged['ratio'] = merged['Choice_A'] / (
        merged['Choice_A'] + merged['Choice_B'])

    # Plot the map, coloring by the 'ratio' column
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    merged.plot(
        column='ratio', ax=ax, legend=True, cmap='coolwarm',
        legend_kwds={'label': "Choice A Rate", 'orientation': "horizontal"})

    plt.title('Referendum Results by Region')
    plt.show()
    return merged


if __name__ == "__main__":

    # Load the data
    referendum, df_reg, df_dep = load_data()

    # Merge the regions and departments data
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep)

    # Merge referendum data with regions and departments
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments)

    # Compute the referendum results aggregated by regions
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas)

    # Print the referendum results by region
    print(referendum_results)

    # Plot the referendum results on a map
    plot_referendum_map(referendum_results)