"""
Plotting referendum results in pandas.

In short, we want to make a beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
<https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/
blob/main/example_map.png>

To do that, you will load the data as pandas.DataFrame, merge the info, and
aggregate them by regions. Finally, plot them on a map using `geopandas`.
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
    """
    Merge regions and departments into one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Rename columns if necessary to ensure compatibility
    if 'region_code' in regions.columns:
        regions = regions.rename(columns={'region_code': 'code_reg'})
    if 'region_name' in regions.columns:
        regions = regions.rename(columns={'region_name': 'name_reg'})
    if 'department_code' in departments.columns:
        departments = departments.rename(columns={'department_code': 'code_dep'})
    if 'department_name' in departments.columns:
        departments = departments.rename(columns={'department_name': 'name_dep'})

    # Perform the merge operation
    merged = departments.merge(regions, on='code_reg', how='left')

    # Ensure the resulting DataFrame has the expected columns
    merged = merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return merged



def merge_referendum_and_areas(referendum, regions_and_departments):
    """
    Merge referendum and regions_and_departments into one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    French living abroad if they are not in the departments DataFrame.

    The merged DataFrame should have no missing values.
    """
    # Ensure 'Department code' is a string for consistent merging
    referendum['Department code'] = referendum['Department code'].astype(str)
    regions_and_departments['code_dep'] = regions_and_departments['code_dep'].astype(str)

    # Merge the referendum data with regions_and_departments
    merged = referendum.merge(
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='inner'
    )

    # Drop rows with missing values to meet the assignment requirements
    merged = merged.dropna()

    return merged



def compute_referendum_result_by_regions(referendum_and_areas):
    """
    Return a table with the absolute count for each region.

    The DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Group by 'code_reg' and 'name_reg' and sum the required columns
    grouped = referendum_and_areas.groupby(
        ['code_reg', 'name_reg']
    )[['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].sum()

    # Reset index to ensure 'code_reg' is used as the final index
    grouped = grouped.reset_index().set_index('code_reg')

    # Rearrange columns to meet the required order
    grouped = grouped[
        ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    ]
    return grouped



def plot_referendum_map(referendum_result_by_regions):
    """
    Plot a map with the referendum results.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Display the result map where the color represents the rate of 'Choice A' over
      all expressed ballots (Choice A + Choice B).
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    import geopandas as gpd
    import matplotlib.pyplot as plt

    # Load the GeoJSON file for regions
    gdf = gpd.read_file('data/regions.geojson')

    # Merge the GeoDataFrame with referendum results
    gdf_merged = gdf.merge(
        referendum_result_by_regions,
        left_on='nom',
        right_on='name_reg',
        how='left'
    )

    # Ensure there are no NaN values in key columns
    if gdf_merged['Choice A'].isnull().any() or gdf_merged['Choice B'].isnull().any():
        raise ValueError("Missing data in the merged GeoDataFrame. Check for unmatched regions.")

    # Compute the ratio of Choice A votes to total votes
    gdf_merged['ratio'] = gdf_merged['Choice A'] / (gdf_merged['Choice A'] + gdf_merged['Choice B'])

    # Create a figure for the map
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Plot the map
    gdf_merged.plot(
        column='ratio',          # The column to use for the color
        cmap='OrRd',             # Colormap
        linewidth=0.8,           # Line width for region borders
        edgecolor='0.8',         # Edge color for region borders
        ax=ax,                   # Axis to plot on
        legend=True,             # Show legend
        legend_kwds={
            'label': "Ratio of Choice A Votes",  # Legend label
            'orientation': "horizontal"         # Legend orientation
        }
    )

    # Add a title and remove axes for a clean look
    ax.set_title("Referendum Results by Region", fontsize=16, pad=20)
    ax.set_axis_off()

    return gdf_merged

if __name__ == "__main__":
    # Load data from CSV files
    referendum, df_reg, df_dep = load_data()

    # Merge regions and departments
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)

    # Merge referendum data with geographical areas
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )

    # Compute referendum results aggregated by regions
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    # Plot the referendum results on a map
    gdf_referendum = plot_referendum_map(referendum_results)
    plt.show()
