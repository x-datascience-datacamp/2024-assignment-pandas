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
    root = "E:/M1/datacamps/2024-assignment-pandas/data/"
    referendumPath = root + "referendum.csv"
    regionsPath = root + "regions.csv"
    departmentsPath = root + "departments.csv"
    referendum = pd.DataFrame(pd.read_csv(referendumPath, delimiter=";"))
    regions = pd.DataFrame(pd.read_csv(regionsPath))
    departments = pd.DataFrame(pd.read_csv(departmentsPath))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Perform the merge
    merged_df = pd.merge(
        departments,
        regions,
        left_on='region_code',
        right_on='code',
        suffixes=('_dep', '_reg')
    )

    # Select and rename the desired columns
    resultColumns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    result = merged_df[resultColumns].rename(
        columns={
            'code_dep': 'code_dep',
            'name_dep': 'name_dep',
            'code_reg': 'code_reg',
            'name_reg': 'name_reg',
        }
    )
    return result


def merge_referendum_and_areas(referendum, regions_and_departments):
    """
    Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Filter out DOM-TOM-COM and French living abroad
    # Generate codes from '01' to '95'
    mainland_codes = [f"{i:02}" for i in range(1, 96)]
    referendum = referendum[
        referendum['Department code'].astype(str).isin(mainland_codes)
        ].copy()

    # Ensure data types match for merging
    referendum.loc[:, 'Department code'] = referendum[
        'Department code'
        ].astype(str)
    regions_and_departments.loc[:, 'code_dep'] = regions_and_departments[
        'code_dep'].astype(str)

    # Perform the merge
    merged_df = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        suffixes=('', '_region')
    )

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """
    Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Group by 'code_reg' and compute the sum of numeric columns
    grouped = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()

    # Set 'code_reg' as the index
    grouped.set_index('code_reg', inplace=True)

    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """
    Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load geographic data for regions
    geoPath = "E:/M1/datacamps/2024-assignment-pandas/data/regions.geojson"
    geo_data = gpd.read_file(geoPath)

    # Compute the ratio of 'Choice A' over total expressed votes
    # (Choice A + Choice B)
    referendum_result_by_regions['ratio'] = (
        referendum_result_by_regions['Choice A'] /
        (
            referendum_result_by_regions['Choice A'] +
            referendum_result_by_regions['Choice B']
            )
    )

    # Merge the geographic data with the referendum results
    merged_data = geo_data.merge(
        referendum_result_by_regions,
        left_on='code',
        right_on='code_reg'
    )

    # Plot the map with the 'ratio' column
    merged_data.plot(
        column='ratio',
        cmap='coolwarm',
        legend=True,
        legend_kwds={'label': "Rate of Choice A"},
        figsize=(10, 10)
    )

    plt.title("Referendum Results: Rate of Choice A by Region", fontsize=16)
    plt.axis('off')

    # Return the merged GeoDataFrame
    return merged_data


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
