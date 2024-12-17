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
    merged_data = pd.merge(regions, departments,
                           left_on="code", right_on="region_code",
                           suffixes=('_reg', '_dep'))
    return merged_data[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    ref_filter = referendum[~referendum["Department code"].str.startswith("Z")]
    dep_code = ref_filter["Department code"]
    for i in range(len(dep_code)):
        if len(dep_code[i])==1:
            ref_filter["Department code"][i] = "0"+dep_code[i]
    merged_data = pd.merge(regions_and_departments, ref_filter,
                           left_on="code_dep", right_on="Department code",
                           how="inner")
    return merged_data


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas[['name_reg',
                                                 'Registered',
                                                 'Abstentions',
                                                 'Null',
                                                 'Choice A',
                                                 'Choice B']]
    return referendum_and_areas.groupby(['name_reg'], as_index = False).sum()


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("data/regions.geojson")
    ref_res_regions_coor = pd.merge(referendum_result_by_regions,
                                              gdf,
                                              left_on="name_reg", right_on="nom")
    ref_res_regions_coor = gpd.GeoDataFrame(ref_res_regions_coor)
    print(ref_res_regions_coor.plot("Choice A", legend=True))
    ref_res_regions_coor["ratio"] = ref_res_regions_coor["Choice A"] / ref_res_regions_coor[["Choice A", "Choice B"]].sum(axis=1)
    return ref_res_regions_coor


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
