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
    referendum_file = "./data/referendum.csv"
    regions_file = "./data/regions.csv"
    departments_file = "./data/departments.csv"

    # Load the CSV files into DataFrames
    referendum = pd.read_csv(referendum_file, sep=";")
    regions = pd.read_csv(regions_file)
    departments = pd.read_csv(departments_file)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments['code'] = departments['code'].astype(str).str.lstrip('0')

    merged_df = pd.merge(regions, departments, left_on='code',
                         right_on='region_code', suffixes=('_reg', '_dep'))

    return merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    merged_df = pd.merge(referendum, regions_and_departments,
                         left_on='Department code', right_on='code_dep',
                         how='inner')
    merged_df = merged_df[~merged_df['Department code'].str.startswith('Z')]

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    aggregated = (
        referendum_and_areas.groupby(['code_reg', 'name_reg'])[cols]
        .sum()
        .reset_index()
    )

    # Set 'code_reg' as the index
    aggregated.set_index('code_reg', inplace=True)
    return aggregated


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("data/regions.geojson")
    merged = pd.merge(
        gdf,
        referendum_result_by_regions,
        how="left",
        left_on="code",
        right_on="code_reg",
    )
    merged["ratio"] = merged["Choice A"] / (
        merged["Choice A"] + merged["Choice B"]
    )
    merged = gpd.GeoDataFrame(merged)
    merged.plot(column="ratio", legend=True, cmap="RdYlBu")
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
