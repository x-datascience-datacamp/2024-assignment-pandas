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
    referendum = pd.read_csv("data/referendum.csv", delimiter=";")
    regions = pd.read_csv("data/regions.csv", delimiter=",")
    departments = pd.read_csv("data/departments.csv", delimiter=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Merge regions and departments
    # regions.code == departments.region_code
    departments = departments.rename(
        columns={
            'code': 'code_dep',
            'region_code': 'code_reg',
            'name': 'name_dep'
        }
    )
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    result = pd.merge(regions, departments, on='code_reg', how='right')
    return result[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    ref = referendum.copy()
    reg_and_dep = regions_and_departments.copy()
    reg_and_dep['code_dep'] = reg_and_dep[
        'code_dep'].str.lstrip('0')
    res = ref.merge(
        reg_and_dep,
        left_on='Department code',
        right_on='code_dep')
    res = res.drop(res[res['code_dep'].isin(
        ['COM', 'TOM', 'DOM']) | res['Department code'] == 'ZZ'].index)
    res.dropna(inplace=True)
    return res


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    count = referendum_and_areas.groupby('code_reg').agg(
        {
            'name_reg': 'first',
            'Registered': 'sum',
            'Abstentions': 'sum',
            'Choice A': 'sum',
            'Choice B': 'sum',
            'Null': 'sum',
        }
    )
    return count


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geos = gpd.read_file("data/regions.geojson")
    res = geos.merge(
        referendum_result_by_regions,
        how="left",
        right_on="code_reg",
        left_on="code"
    )
    res['ratio'] = res['Choice A'] / (
        res['Choice A'] + res['Choice B'])
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    res.plot(
        column='ratio',
        legend=True,
        ax=ax,
    )
    plt.title("Rate of 'Choice A' over all expressed ballots")
    plt.axis('off')
    plt.show()
    return gpd.GeoDataFrame(res, geometry=geos.geometry)


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
