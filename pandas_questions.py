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
    """Load data from the CSV files referendum, regions, and departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = departments.merge(
        regions,
        left_on="region_code",
        right_on="code",
        suffixes=("_dep", "_reg")
    )
    merged_df = merged_df[["code_reg", "name_reg", "code_dep", "name_dep"]]
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame."""
    temp = referendum["Department code"].astype(str).str.strip()
    referendum["Department code"] = temp.str.zfill(2)

    temp2 = regions_and_departments["code_dep"].astype(str).str.strip()
    regions_and_departments["code_dep"] = temp2.str.zfill(2)

    referendum_filtered = referendum[
        ~referendum["Department code"].str.startswith(("97", "98", "99"))
    ]

    merged_df = referendum_filtered.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner"
    )

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby(["code_reg", "name_reg"]).sum()
    grouped = grouped[[
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B"
    ]]

    return grouped.reset_index().set_index("code_reg")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file("data/regions.geojson")

    # Merge with referendum results
    merged_gdf = regions_geo.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True
    )

    ratChoice = (merged_gdf["Choice A"] + merged_gdf["Choice B"])
    merged_gdf["ratio"] = merged_gdf["Choice A"] / ratChoice

    # Plot the map
    ax = merged_gdf.plot(column="ratio", legend=True, cmap="Blues")
    ax.set_title("Referendum Results: Choice A Ratio by Region")

    return merged_gdf


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
