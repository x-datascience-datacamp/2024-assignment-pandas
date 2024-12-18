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
    referendum = pd.read_csv(r"data\referendum.csv", sep=";")
    regions = pd.read_csv(r"data\regions.csv")
    departments = pd.read_csv(r"data\departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # rename column names
    renamed_deparmtments = departments.rename(columns={
        'code': 'code_dep',
        'slug': 'name_dep',
        'region_code': 'code_reg'
    })
    renamed_regions = regions.rename(columns={
        'code': 'code_reg',
        'name': 'name_reg'
    })
    # merge data
    merged_df = renamed_deparmtments.merge(
        renamed_regions,
        on='code_reg',
        how='left'
    )
    # order of columns
    final_df = merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return final_df


def safe_convert(value):
    try:
        return int(value)  # 尝试转换为整数
    except ValueError:
        return value  # 如果失败，返回原始值


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # transform code column type to int
    regions_and_departments['code_dep'] = regions_and_departments['code_dep'].apply(safe_convert)
    # drop the lines relative to DOM-TOM-COM departments
    referendum = referendum[:36565]
    referendum.loc[:, 'Department code'] = referendum['Department code'].apply(safe_convert)

    # #rename column names
    # rename_referendum = referendum.rename(columns = {
    #     'Department code': 'code_dep'
    # })
    # merge data
    merged_df = referendum.merge(
        regions_and_departments,
        right_on='code_dep',
        left_on='Department code',
        how='left'
    )
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas_selected = referendum_and_areas[['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    referendum_and_areas_selected.head(50)
    # grouped by name_reg and summation
    referendum_and_areas_selected = referendum_and_areas_selected.groupby('name_reg', as_index=False).sum()
    return referendum_and_areas_selected


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # 1. Load geographic data
    geo_data = gpd.read_file(r"data\regions.geojson")
    # 2. Calculate the ratio of 'Choice A' over all expressed ballots
    referendum_result_by_regions['ratio'] = (
        referendum_result_by_regions['Choice A'] /
        (referendum_result_by_regions['Choice A']
         + referendum_result_by_regions['Choice B']
         )
    )
    # Step 3: Merge the geographic data with referendum results
    merged_data = geo_data.merge(
        referendum_result_by_regions,
        left_on='nom',
        right_on='name_reg',
        how='left'
    )
    # Step 4: Plot the map
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    merged_data.plot(
        column='ratio',         # Column to color the regions
        cmap='coolwarm',        # Color map for visualization
        legend=True,            # Add a legend to the map
        legend_kwds={'label': "Proportion of 'Choice A' Votes"},
        ax=ax
    )
    plt.title("Referendum Results by Region", fontsize=15)
    plt.axis('off')  # Hide axes for better visualization
    plt.show()
    # Step 5: Return the GeoDataFrame with results
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
