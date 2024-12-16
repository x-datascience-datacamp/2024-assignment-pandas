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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    dep = departments.rename(columns={"region_code": "code_reg",
                                      "code": "code_dep", "name": "name_dep"})
    res = pd.merge(reg[["code_reg", "name_reg"]],
                   dep[["code_reg", "code_dep",
                        "name_dep"]])[["code_reg", "name_reg",
                                       "code_dep", "name_dep"]]
    return res


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    reg_dep = regions_and_departments
    reg_dep = reg_dep.drop(
        index=reg_dep[reg_dep["code_reg"] == "COM"].index)
    reg_dep["code_dep"] = reg_dep["code_dep"].apply(
        lambda x: x[1] if x[0] == "0" else x)
    ref = referendum.drop(
        index=referendum[referendum["Department name"] ==
                         "FRANCAIS DE L'ETRANGER"].index)
    ref["code_dep"] = ref["Department code"]
    reg_dep_ref = pd.merge(reg_dep, ref)

    return reg_dep_ref


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    ref_per_reg = referendum_and_areas[['code_reg',
                                        'Registered',
                                        'Abstentions',
                                        'Null',
                                        'Choice A',
                                        'Choice B']].groupby("code_reg").sum()
    reg_name = referendum_and_areas[["code_reg", "name_reg"]]
    reg_name = reg_name.set_index("code_reg").drop_duplicates()
    results = pd.merge(reg_name, ref_per_reg, on="code_reg")

    return results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodata = gpd.read_file("data/regions.geojson")
    geodata = geodata.rename(columns={"code": "code_reg"})
    geodata = geodata.set_index("code_reg")
    georesults = pd.merge(referendum_result_by_regions, geodata, on="code_reg")
    georesults = gpd.GeoDataFrame(georesults)
    georesults["ratio"] = georesults["Choice A"] / \
        (georesults["Choice A"] + georesults["Choice B"])

    return georesults


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
