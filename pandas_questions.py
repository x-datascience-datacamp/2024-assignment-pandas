"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using geopandas.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os


# def load_data():
#     """Load data from the CSV files referundum/regions/departments."""
#     referendum = pd.DataFrame({})
#     regions = pd.DataFrame({})
#     departments = pd.DataFrame({})

#     return referendum, regions, departments

def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", delimiter=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['
    _reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = departments.merge(
        regions, how="left", left_on="region_code", right_on="code"
    )
    merged = merged.rename(
        columns={
            "code_x": "code_dep",
            "name_x": "name_dep",
            "code_y": "code_reg",
            "name_y": "name_reg",
        }
    )
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]

def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    merged = referendum.merge(
        regions_and_departments, how="inner", left_on="Department code", right_on="code_dep"
    )
    excluded_deps = ["971", "972", "973", "974", "976", "984"]
    merged = merged[~merged["code_dep"].isin(excluded_deps)]
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by code_reg and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    aggregated = referendum_and_areas.groupby(
        ["code_reg", "name_reg"]
    ).agg(
        {
            "Registered": "sum",
            "Abstentions": "sum",
            "Null": "sum",
            "Choice A": "sum",
            "Choice B": "sum",
        }
    )
    return aggregated.reset_index().set_index("code_reg")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from regions.geojson.
    * Merge these info into referendum_result_by_regions.
    * Use the method GeoDataFrame.plot to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("data/regions.geojson")
    merged = geo_data.merge(
        referendum_result_by_regions,
        how="left",
        left_on="code",
        right_on="code_reg",
    )
    merged["ratio"] = merged["Choice A"] / (
        merged["Choice A"] + merged["Choice B"]
    )

    ax = merged.plot(
        column="ratio",
        cmap="viridis",
        legend=True,
        legend_kwds={"label": "Proportion of Choice A"},
        figsize=(10, 8),
    )
    ax.set_title("Referendum Results by Region")
    plt.axis("off")
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
