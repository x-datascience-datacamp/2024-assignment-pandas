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
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("./data/referendum.csv", sep=';')
    regions = pd.read_csv("./data/regions.csv")
    departments = pd.read_csv("./data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = pd.merge(
        regions, departments, left_on='code', right_on='region_code'
    )
    # Rename columns to ensure clarity
    merged.columns = ['id_x', 'code_reg', 'name_reg', 'slug_x', 'id_y',
                      'region_code', 'code_dep', 'name_dep', 'slug_y']
    # Select only required columns
    return merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    French living abroad.
    """
    # Handle leading zeros in code_dep
    def replace_useless_zero(row):
        return row.lstrip('0') if row.startswith('0') else row

    regions_and_departments['code_dep'] = regions_and_departments['code_dep'].apply(replace_useless_zero)
    # Filter out irrelevant departments
    referendum = referendum[~referendum["Department code"].str.startswith('Z')]

    # Merge and return the combined DataFrame
    merged = pd.merge(
        referendum, regions_and_departments,
        left_on="Department code", right_on="code_dep"
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    selected = ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    # Aggregate data by regions
    counts = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum',
    })
    return counts[selected]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load geographic data
    geodata = gpd.read_file("./data/regions.geojson")
    # Ensure referendum result has code column for merging
    referendum_result_by_regions["code"] = referendum_result_by_regions.index
    merged = pd.merge(geodata, referendum_result_by_regions, on='code')

    # Calculate 'ratio' and convert to GeoDataFrame
    merged['ratio'] = merged['Choice A'] / (merged['Choice A'] + merged['Choice B'])
    merged = gpd.GeoDataFrame(merged)

    # Plot the map
    merged.plot(
        column="ratio",
        cmap='coolwarm',
        legend=True,
        legend_kwds={'label': "Proportion of Choice A"}
    )
    plt.show()

    return merged


if __name__ == "__main__":
    # Load datasets
    referendum, df_reg, df_dep = load_data()

    # Merge regions and departments
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )

    # Merge referendum results with areas
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )

    # Compute referendum results by regions
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    # Plot referendum results on a map
    plot_referendum_map(referendum_results)
