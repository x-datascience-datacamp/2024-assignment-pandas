"""
This module provides functions to load and analyze referendum data,
merge with regional information, and produce a geographic visualization.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data(
    referendum_path='data/referendum.csv',
    regions_path='data/regions.csv',
    departments_path='data/departments.csv'
):
    """
    Load referendum, regions, and departments data from CSV files.

    Parameters
    ----------
    referendum_path : str
        Path to the referendum CSV file.
    regions_path : str
        Path to the regions CSV file.
    departments_path : str
        Path to the departments CSV file.

    Returns
    -------
    referendum : pd.DataFrame
        DataFrame with referendum results.
    regions : pd.DataFrame
        DataFrame with regions data.
    departments : pd.DataFrame
        DataFrame with departments data.
    """
    referendum = pd.read_csv(referendum_path, sep=';')
    regions = pd.read_csv(regions_path)
    departments = pd.read_csv(departments_path)
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """
    Merge regions and departments into a single DataFrame.

    Parameters
    ----------
    regions : pd.DataFrame
        DataFrame with regional data.
    departments : pd.DataFrame
        DataFrame with departmental data.

    Returns
    -------
    merged : pd.DataFrame
        A DataFrame with columns:
        ['code_reg', 'name_reg', 'code_dep', 'name_dep'].
    """
    merged = pd.merge(
        regions,
        departments,
        left_on='code',
        right_on='region_code',
        how='left'
    )

    merged.columns = [
        'id_reg', 'code_reg', 'name_reg', 'slug_reg',
        'id_dep', 'region_code', 'code_dep', 'name_dep', 'slug_dep'
    ]

    return merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """
    Merge the referendum data with the merged regions/departments data.

    Excludes DOM-TOM-COM departments and French living abroad (department codes
    starting with 'Z').

    Parameters
    ----------
    referendum : pd.DataFrame
        The referendum DataFrame.
    regions_and_departments : pd.DataFrame
        A DataFrame that maps departments to their regions.

    Returns
    -------
    merged : pd.DataFrame
        Merged DataFrame with referendum data and associated region and
        department info.
    """
    # Filter out rows where department code starts with 'Z'
    referendum = referendum[~referendum["Department code"].str.startswith('Z')]

    # Remove leading zeros to match department codes
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].str.lstrip('0')
    )

    merged = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="left"
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """
    Compute the aggregated referendum results by region.

    Parameters
    ----------
    referendum_and_areas : pd.DataFrame
        DataFrame with referendum results and associated region/department.

    Returns
    -------
    aggregated : pd.DataFrame
        DataFrame indexed by `code_reg` with columns:
        ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A',
         'Choice B'].
    """
    grouped = referendum_and_areas.groupby("code_reg").agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })

    columns_order = [
        'name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B'
    ]
    return grouped[columns_order]


def plot_referendum_map(referendum_result_by_regions):
    """
    Plot a map with the referendum results by region.

    Parameters
    ----------
    referendum_result_by_regions : pd.DataFrame
        Aggregated referendum results by region.

    Returns
    -------
    merged_geo : gpd.GeoDataFrame
        GeoDataFrame with a 'ratio' column representing the 'Choice A' rate
        over expressed ballots.
    """
    geojson_path = 'data/regions.geojson'
    geodata = gpd.read_file(geojson_path)

    # Create a 'code' column in results to merge on
    referendum_result_by_regions["code"] = referendum_result_by_regions.index

    merged_geo = pd.merge(
        geodata,
        referendum_result_by_regions,
        on='code',
        how='left'
    )

    expressed = merged_geo["Choice A"] + merged_geo["Choice B"]
    sum_expr = expressed.where(expressed != 0, 1)
    merged_geo['ratio'] = merged_geo['Choice A'] / sum_expr
    merged_geo = gpd.GeoDataFrame(merged_geo)
    merged_geo.plot(column="ratio", legend=True, cmap='RdYlGn')

    plt.title("Referendum Results: Choice A Ratio by Region")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.show()

    return merged_geo


if __name__ == "__main__":
    referendum, regions, departments = load_data()
    regions_and_deps = merge_regions_and_departments(regions, departments)
    ref_and_areas = merge_referendum_and_areas(referendum, regions_and_deps)

    referendum_results = compute_referendum_result_by_regions(ref_and_areas)
    print(referendum_results)
    plot_referendum_map(referendum_results)
