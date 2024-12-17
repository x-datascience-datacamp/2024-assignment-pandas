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
    referendum = pd.read_csv("data/referendum.csv",
                             sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    # referendum = pd.DataFrame({ref})
    # regions = pd.DataFrame({reg})
    # departments = pd.DataFrame({dep})

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.
    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions.rename(columns={"name": "name_reg"}, inplace=True)
    departments.rename(columns={"name": "name_dep",
                                "code": "code_dep"},
                       inplace=True)
    regions_and_departments = pd.merge(regions, departments,
                                       left_on=["code"],
                                       right_on=["region_code"])
    regions_and_departments.rename(columns={"region_code": "code_reg"},
                                   inplace=True)
    regions_and_departments = regions_and_departments[["code_reg", "name_reg",
                                                       "code_dep", "name_dep"]]

    return regions_and_departments
    # return pd.DataFrame({regions_and_departments})


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    values_to_drop = ["GUADELOUPE", "MARTINIQUE", "GUYANE", "LA REUNION",
                      "MAYOTTE", "NOUVELLE CALEDONIE", "POLYNESIE FRANCAISE",
                      "SAINT PIERRE ET MIQUELON", "WALLIS-ET-FUTUNA",
                      "SAINT-MARTIN/SAINT-BARTHELEMY",
                      "FRANCAIS DE L'ETRANGER"]
    to_drop = referendum[
              referendum["Department name"].isin(values_to_drop)].index
    referendum.drop(to_drop, inplace=True)
    referendum_and_areas = pd.merge(referendum,
                                    regions_and_departments,
                                    left_on="Department code",
                                    right_on="code_dep")

    return referendum_and_areas
    # return pd.DataFrame({referendum_and_areas})


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    referendum_result_by_regions = referendum_and_areas.groupby(["code_reg",
                                                                 "name_reg"])[['Registered',
                                                                               'Abstentions', 'Null',
                                                                               'Choice A', 'Choice B']].sum()
    return referendum_result_by_regions
    # return pd.DataFrame({referendum_result_by_regions})


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_data = gpd.read_file('data/regions.geojson')
    referendum_result_by_regions = referendum_result_by_regions.copy()
    referendum_result_by_regions['ratio'] = (
        referendum_result_by_regions['Choice A'] /
        (referendum_result_by_regions['Choice A'] +
         referendum_result_by_regions['Choice B'] +
         referendum_result_by_regions['Null'])
    )
    merged_data = geo_data.merge(referendum_result_by_regions,
                                 left_on='code',
                                 right_on='code_reg',
                                 how='left')
    ax = merged_data.plot(column='ratio',
                          cmap='Blues',
                          legend=True,
                          figsize=(10, 6),
                          edgecolor='black')
    ax.set_title("Ratio of 'Choice A' in the Referendum by Region")

    return merged_data, ax
    # return gpd.GeoDataFrame({})


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
    