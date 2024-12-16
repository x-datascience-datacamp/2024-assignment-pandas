import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data(referendum_path, regions_path, departments_path):
    """Load data from the CSV files referendum, regions, and departments.

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
        DataFrame containing referendum results.
    regions : pd.DataFrame
        DataFrame containing regions information.
    departments : pd.DataFrame
        DataFrame containing departments information.
    """
    referendum = pd.read_csv(referendum_path, sep=";")
    regions = pd.read_csv(regions_path, sep=",")
    departments = pd.read_csv(departments_path, sep=",")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Rename columns for clarity and merging
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(
        columns={"code": "code_dep", "name": "name_dep", "region_code": "code_reg"}
    )

    # Merge departments with regions
    merged = pd.merge(departments, regions, on="code_reg", how="left")

    # Select required columns
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum data and region/department data.

    Drop DOM-TOM-COM departments and French living abroad.

    Parameters
    ----------
    referendum : pd.DataFrame
        Referendum data with department codes.
    regions_and_departments : pd.DataFrame
        Merged regions and departments data.

    Returns
    -------
    merged : pd.DataFrame
        DataFrame combining referendum results and region/department areas.
    """
    # Filter mainland France departments (codes 01 to 95)
    mainland_departments = regions_and_departments[
        regions_and_departments["code_dep"].str.match(r"^[0-9]{2,3}$")
    ]

    # Merge referendum data with filtered mainland departments
    merged = pd.merge(
        referendum, mainland_departments, left_on="Department code", right_on="code_dep"
    )

    # Drop redundant column
    return merged.drop(columns=["code_dep"])


def compute_referendum_result_by_regions(referendum_and_areas):
    """Compute aggregated referendum results for each region.

    Parameters
    ----------
    referendum_and_areas : pd.DataFrame
        DataFrame combining referendum results and geographic areas.

    Returns
    -------
    result : pd.DataFrame
        Aggregated referendum results by region.
    """
    # Group data by 'code_reg' and 'name_reg', summing up numerical columns
    grouped = referendum_and_areas.groupby(["code_reg", "name_reg"]).sum()

    # Select required columns and reset the index
    result = grouped[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ].reset_index()

    # Set 'code_reg' as the index
    return result.set_index("code_reg")


def plot_referendum_map(referendum_result_by_regions, geojson_path):
    """Plot a map with the results from the referendum.

    Parameters
    ----------
    referendum_result_by_regions : pd.DataFrame
        Referendum results aggregated by region.
    geojson_path : str
        Path to the regions.geojson file.

    Returns
    -------
    merged : gpd.GeoDataFrame
        GeoDataFrame with geographic data and referendum ratios.
    """
    # Load geographic data
    geo_regions = gpd.read_file(geojson_path)

    # Merge referendum results with geographic data
    merged = geo_regions.merge(
        referendum_result_by_regions, left_on="code", right_index=True
    )

    # Compute the ratio of 'Choice A' over all expressed votes
    merged["ratio"] = merged["Choice A"] / (merged["Choice A"] + merged["Choice B"])

    # Plot the map
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    merged.plot(
        column="ratio",
        cmap="coolwarm",
        legend=True,
        legend_kwds={"label": "Choice A Ratio", "orientation": "horizontal"},
        ax=ax,
    )
    plt.title("Referendum Results: Choice A Ratio by Region")
    return merged


if __name__ == "__main__":
    # Define file paths
    referendum_path = "data/referendum.csv"
    regions_path = "data/regions.csv"
    departments_path = "data/departments.csv"
    geojson_path = "data/regions.geojson"

    # Load the data
    referendum, regions, departments = load_data(
        referendum_path, regions_path, departments_path
    )

    # Merge regions and departments
    regions_and_departments = merge_regions_and_departments(regions, departments)

    # Merge referendum results with areas
    referendum_and_areas = merge_referendum_and_areas(referendum, regions_and_departments)

    # Compute aggregated results by region
    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)

    print("Referendum Results by Region:")
    print(referendum_results)

    # Plot the referendum map
    referendum_geo = plot_referendum_map(referendum_results, geojson_path)
    plt.show()
