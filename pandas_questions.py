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
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Rename columns
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep"
        }
    )

    # Merge on "code_reg"
    merged = departments.merge(regions, how="left", on="code_reg")
    merged = merged[["code_reg", "name_reg", "code_dep", "name_dep"]]
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Format the department code
    referendum["Department code"] = (
        referendum["Department code"].astype(str).str.zfill(2)
    )
    regions_and_departments["code_dep"] = regions_and_departments[
        "code_dep"
    ].astype(str)

    # Filter out DOM-TOM-COM departments and foreign regions
    referendum_filtered = referendum[
        ~referendum["Department code"].str.startswith('Z')
    ]

    # Merge DataFrames
    merged = referendum_filtered.merge(
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='inner'
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Group by region code and name, then sum relevant columns
    agg = referendum_and_areas.groupby(
        ["code_reg", "name_reg"], as_index=False
    )[["Registered", "Abstentions", "Null", "Choice A", "Choice B"]].sum()

    # Set the index to region code
    agg = agg.set_index("code_reg")
    return agg


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load geographic data
    gdf_regions = gpd.read_file("data/regions.geojson")

    # Merge referendum results with geographic data
    merged_gdf = gdf_regions.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True,
        how="left"
    )

    # Calculate the ratio of votes for Choice A
    merged_gdf["ratio"] = merged_gdf["Choice A"] / (
        merged_gdf["Choice A"] + merged_gdf["Choice B"]
    )

    # Plot the map with the calculated ratio
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    merged_gdf.plot(
        column="ratio",
        ax=ax,
        legend=True,
        cmap="RdYlGn",
        edgecolor="black"
    )
    ax.set_title("Referendum Results by Region (Choice A ratio)")
    ax.set_axis_off()

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
