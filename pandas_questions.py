# -*- coding: utf-8 -*-
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", delimiter=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
        }
    )

    merged = departments.merge(regions, on="code_reg", how="right")
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    French living abroad.
    """

    def standardize_department_code(code):
        if code.isnumeric():
            return code.zfill(2)  # Zero-pad numeric codes
        return code

    referendum["Department code"] = referendum["Department code"].apply(
        standardize_department_code
    )
    # Merge and resolve column name conflicts
    merged = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = (
        referendum_and_areas.groupby(["code_reg", "name_reg"])
        .sum(numeric_only=True)
        .reset_index()
    )
    result = grouped[
        [
            "code_reg",
            "name_reg",
            "Registered",
            "Abstentions",
            "Null",
            "Choice A",
            "Choice B",
        ]
    ]

    # Ensure all regions are included
    all_regions = referendum_and_areas[
        ["code_reg", "name_reg"]
    ].drop_duplicates()

    # Join with explicit suffixes to avoid overlap
    result = (
        all_regions.merge(result, how="inner", on=["code_reg", "name_reg"])
        .fillna(0)
        .set_index("code_reg")
    )
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("data/regions.geojson")
    geo_data = geo_data.rename(columns={"code": "code_reg"})

    # Compute the ratio for 'Choice A'
    referendum_result_by_regions["ratio"] = referendum_result_by_regions[
        "Choice A"
    ] / (
        referendum_result_by_regions["Choice A"]
        + referendum_result_by_regions["Choice B"]
    )

    merged = geo_data.merge(referendum_result_by_regions, on="code_reg")

    # Plot
    merged.plot(column="ratio", legend=True, cmap="coolwarm")
    plt.title("Referendum Results: Choice A Ratio by Region")

    return merged


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
