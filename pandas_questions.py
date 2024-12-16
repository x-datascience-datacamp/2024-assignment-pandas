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
    referendum = pd.read_csv('data/referendum.csv', delimiter=';')
    regions = pd.read_csv('data/regions.csv', delimiter=',')
    departments = pd.read_csv('data/departments.csv', delimiter=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = pd.merge(
        regions,
        departments,
        left_on='code',
        right_on='region_code',
        how='inner'
        )

    regions_and_departments = regions_and_departments.drop(
        ['slug_x', 'id_x', 'id_y', 'slug_y', 'region_code'], axis=1
        )
    regions_and_departments = regions_and_departments.rename(
        columns={'name_x': 'name_reg',
                 'name_y': 'name_dep',
                 'code_x': 'code_reg',
                 'code_y': 'code_dep'}
        )

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: f'0{x}' if x.isdigit() and 0 <= int(x) <= 9 else x
        )
    referendum_and_areas = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='inner'
        )

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Group by 'code_reg' and aggregate the required columns
    result = (
        referendum_and_areas.groupby('code_reg')
        .agg({
            'name_reg': 'first',  # Take the first (unique for each region)
            'Registered': 'sum',
            'Abstentions': 'sum',
            'Null': 'sum',
            'Choice A': 'sum',
            'Choice B': 'sum'
        }).reset_index()  # Reset index
    )
    # Optionally, set 'code_reg' as the index
    result.set_index('code_reg', inplace=True)
    return result


def plot_referendum_map(referendum_result_by_regions):
    """
    Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geographic data
    regions_geo = gpd.read_file('data/regions.geojson')

    # Merge the referendum results with geographic data
    merged = regions_geo.merge(
        referendum_result_by_regions,
        how='left',
        left_on='code',
        right_on='code_reg'
    )

    # Calculate the ratio of 'Choice A' over all expressed ballots
    merged['ratio'] = merged['Choice A'] \
        / (merged['Choice A'] + merged['Choice B'])

    # Plot the map with the 'ratio' column
    ax = merged.plot(
        column='ratio',
        cmap='Blues',
        legend=True,
        figsize=(10, 10)
        )
    ax.set_title(
        "Referendum Results: Ratio of 'Choice A' by Region",
        fontsize=16
        )
    ax.set_axis_off()

    # Show the plot
    plt.show()

    # Return the GeoDataFrame with the ratio column
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
