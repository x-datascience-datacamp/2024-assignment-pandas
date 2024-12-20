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
    
    # Debugging: Print columns to verify
    print("Referendum Columns:", referendum.columns.tolist())
    print("Regions Columns:", regions.columns.tolist())
    print("Departments Columns:", departments.columns.tolist())
    
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments into one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = departments.merge(
        regions,
        left_on='code_reg',  # Column from departments
        right_on='code',     # Column from regions
        how='left'
    )
    merged = merged.rename(columns={'name': 'name_reg'})
    merged = merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments into one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    French living abroad if they are not in the departments DataFrame.
    """
    # Ensure matching department codes
    referendum['Department code'] = referendum['Department code'].astype(str)
    merged = referendum.merge(
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='inner'
    )
    # Ensure no missing values (the provided tests expect a certain shape)
    merged = merged.dropna()
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby(
        ['code_reg', 'name_reg'],
        as_index=False
    )[['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].sum()
    grouped = grouped.set_index('code_reg')
    grouped = grouped[
        ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    ]
    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the referendum results.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Display the result map where the color represents the rate of 'Choice A' over
      all expressed ballots (Choice A + Choice B).
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geojson file of regions
    gdf = gpd.read_file('data/regions.geojson')

    # Debugging: Print columns to verify
    print("GeoDataFrame Columns:", gdf.columns.tolist())

    # Merge on region name
    gdf_merged = gdf.merge(
        referendum_result_by_regions,
        left_on='nom',          # Assuming 'nom' is the region name in GeoDataFrame
        right_on='name_reg',
        how='left'
    )

    # Compute the ratio: Choice A / (Choice A + Choice B)
    choice_a = gdf_merged['Choice A']
    choice_b = gdf_merged['Choice B']
    total_votes = choice_a + choice_b
    gdf_merged['ratio'] = choice_a / total_votes

    # Create a figure and axis for a nicer plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Plot the map with a colormap and a legend
    gdf_merged.plot(
        column='ratio',
        cmap='OrRd',
        linewidth=0.8,
        edgecolor='0.8',
        ax=ax,
        legend=True,
        legend_kwds={
            'label': "Ratio of Choice A Votes",
            'orientation': "horizontal"
        }
    )

    # Add a title and remove axis lines for a cleaner look
    ax.set_title("Referendum Results by Region", fontsize=16, pad=20)
    ax.set_axis_off()

    return gdf_merged


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    gdf_referendum = plot_referendum_map(referendum_results)
    plt.show()
