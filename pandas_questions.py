"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
from operator import index

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv", sep=',')
    departments = pd.read_csv("data/departments.csv", sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.columns = ["id", "code_reg", "name_reg", "slug"]

    departments.columns = ["id", "code_reg", "code_dep", "name_dep", "slug"]

    return pd.merge(regions[["code_reg", "name_reg"]], departments[["code_reg", "code_dep", "name_dep"]],
             on='code_reg', how='right')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    """
    referendum.columns = ["code_dep", 'Department name', 'Town code', 'Town name',
       'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    referendum['code_dep'] = referendum['code_dep'].astype(str)
    regions_and_departments['code_dep'] = regions_and_departments['code_dep'].astype(str)
    """

    referendum['code_dep'] = referendum['Department code'].astype(str)
    for l in range(len(referendum)):
        if len(referendum['code_dep'][l]) == 1:
            referendum.loc[l, 'code_dep'] = str(0) + referendum['code_dep'][l]

    regions_and_departments['code_dep'] = regions_and_departments['code_dep'].astype(str)

    return pd.merge(regions_and_departments, referendum, on='code_dep', how='right').dropna(axis=0, how='any')


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    groups = referendum_and_areas.groupby(referendum_and_areas['code_reg'])

    ref_res = pd.DataFrame(columns=['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B'],
                           index=sorted(list(set(referendum_and_areas['code_reg']))))

    for code_reg in ref_res.index:
        reg = groups.get_group(code_reg)

        ref_res.loc[code_reg] = (reg['name_reg'][reg.index[0]], reg['Registered'].sum(), reg['Abstentions'].sum(), reg['Null'].sum(),
                            reg['Choice A'].sum(), reg['Choice B'].sum())

    return ref_res


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    df_ratio = pd.DataFrame(columns=["code", 'ratio'], index=referendum_result_by_regions.index)
    df_ratio["code"] = referendum_result_by_regions.index
    df_ratio['name_reg'] = referendum_result_by_regions['name_reg']
    for id in df_ratio.index:

        df_ratio.loc[id, 'ratio'] = (referendum_result_by_regions['Choice A'][id] /
                                     referendum_result_by_regions[["Choice A", "Choice B"]].sum(axis=1)[id])
    gdf = gpd.read_file('data/regions.geojson')

    gdf = gdf.merge(df_ratio, on='code')
    gdf.plot(column='ratio', legend=True)

    return gdf


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
