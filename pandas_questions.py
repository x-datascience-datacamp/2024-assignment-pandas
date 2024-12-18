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
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(
        departments,
        regions,
        left_on='region_code',
        right_on='code',
        suffixes=('_dep', '_reg'),
    )
    columns = ['region_code', 'name_reg', 'code_dep', 'name_dep']
    result = df[columns].rename(columns={'region_code': 'code_reg'})
    return result


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    French living abroad.
    """
    filtered = (
        ~regions_and_departments['code_reg'].str.startswith('Z') &
        ~regions_and_departments['code_reg'].str.startswith('reg') &
        ~regions_and_departments['code_reg'].str.startswith('COM') &
        ~regions_and_departments['code_reg'].str.startswith('TOM')
    )
    regions_and_departments = regions_and_departments[filtered]
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].str.lstrip('0')
    )
    merged = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum',
    })
    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geojson_path = 'data/regions.geojson'
    geodata = gpd.read_file(geojson_path)

    referendum_result_by_regions["code"] = referendum_result_by_regions.index

    merged_geo = pd.merge(
        geodata,
        referendum_result_by_regions,
        on='code',
        how='left',
    )

    expressed = merged_geo["Choice A"] + merged_geo["Choice B"]
    sum_expr = expressed.where(expressed != 0, 1)
    merged_geo['ratio'] = merged_geo['Choice A'] / sum_expr
    merged_geo = gpd.GeoDataFrame(merged_geo)
    merged_geo.plot(column="ratio", legend=True, cmap='RdYlGn')

    plt.title("Referendum Results: Choice A Ratio by Region")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.show()

    return merged_geo


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
