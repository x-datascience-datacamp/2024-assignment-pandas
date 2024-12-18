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
    referendum = pd.read_table("./data/referendum.csv", sep=';')
    regions = pd.read_table("./data/regions.csv", sep=',')
    departments = pd.read_table("./data/departments.csv", sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.drop(columns=['id', 'slug'])
    departments = departments.drop(columns=['id', 'slug'])
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(columns={
        "region_code": "code_reg", "name": "name_dep", "code": "code_dep"
        })
    return departments.merge(regions, on="code_reg", how="left")


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum.rename(columns={"Department code": "code_dep"})
    referendum = referendum[referendum['code_dep'].str[0] != 'Z']
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].str.lstrip('0')
    )
    regions_and_departments = regions_and_departments.merge(
        referendum, on="code_dep", how="inner"
    )
    regions_and_departments['Department code'] = referendum['code_dep']
    return regions_and_departments


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas[
        [
            'code_reg',
            'name_reg',
            'Registered',
            'Abstentions',
            'Null',
            'Choice A',
            'Choice B'
        ]
    ]
    referendum_and_areas = referendum_and_areas.groupby(
        ['code_reg', 'name_reg']).sum()
    referendum_and_areas = referendum_and_areas.reset_index()
    referendum_and_areas = referendum_and_areas.set_index('code_reg')

    return referendum_and_areas
def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo = gpd.read_file("./data/regions.geojson")
    geo_small = geo[['geometry']]
    geo_small['code_reg'] = geo['code']
    geo_small = geo_small.set_index('code_reg')
    geo_small = referendum_result_by_regions.join(geo_small)
    geo_small = gpd.GeoDataFrame(geo_small)
    geo_small['ratio'] = geo_small['Choice A'] \
        / (geo_small['Choice A'] + geo_small['Choice B'])
    geo_small.plot('ratio')
    return geo_small


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

    plot_referendum_map(referendum_results)
    plt.show()
