import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("C://Users//Global Computers//Downloads//2024-assignment-pandas//data//referendum.csv", sep=";")
    regions = pd.read_csv("C://Users//Global Computers//Downloads//2024-assignment-pandas//data//regions.csv", sep=",")
    departments = pd.read_csv("C://Users//Global Computers//Downloads//2024-assignment-pandas//data//departments.csv", sep=",")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments into one DataFrame.

    The columns in the final DataFrame will be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = departments.merge(
        regions,
        left_on="region_code",
        right_on="code",
        suffixes=("_dep", "_reg")
    )
    # Keep only relevant columns
    merged = merged[["region_code", "name_reg", "code_dep", "name_dep"]]
    merged.rename(columns={"region_code": "code_reg"}, inplace=True)
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments into one DataFrame.

    Remove data related to:
    - DOM-TOM-COM departments (codes starting with 97 or 98)
    - French living abroad (code_dep == "999")
    """
    # Filter out unwanted data
    filtered_ref = referendum[
        ~referendum["Department code"].str.startswith(("97", "98", "999"))
    ]

    # Merge data
    merged = filtered_ref.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep"
    )

    # Keep relevant columns
    merged = merged[[
        "code_reg", "name_reg", "code_dep", "name_dep",
        "Registered", "Abstentions", "Null", "Choice A", "Choice B"
    ]]
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame is indexed by `code_reg` with columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Group by region code and name
    grouped = referendum_and_areas.groupby(["code_reg", "name_reg"]).sum()

    # Reset index for clarity
    grouped = grouped.reset_index()

    # Keep necessary columns
    grouped = grouped[[
        "code_reg", "name_reg",
        "Registered",
        "Abstentions", "Null", "Choice A", "Choice B"
    ]]

    # Set the region code as index
    grouped.set_index("code_reg", inplace=True)
    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load geographic data from `regions.geojson`.
    * Merge referendum results into geographic data.
    * Compute the ratio 'Choice A' / (Choice A + Choice B).
    * Plot the resulting map.
    """
    # Load geographic data
    geo_data = gpd.read_file("C://Users//Global Computers//Downloads//2024-assignment-pandas//data//regions.geojson")

    # Merge referendum results with geographic data
    merged = geo_data.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True
    )

    # Compute the ratio for Choice A
    merged["ratio"] = merged["Choice A"] / (
        merged["Choice A"] + merged["Choice B"])

    # Plot the map
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    merged.plot(column="ratio", cmap="coolwarm", legend=True,
                legend_kwds={"label": "Ratio of Choice A", "shrink": 0.5},
                ax=ax)
    plt.title("Referendum Results: Ratio of Choice A by Region")
    return merged


if __name__ == "__main__":
    # Load data
    referendum, df_reg, df_dep = load_data()

    # Merge regions and departments
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)

    # Merge referendum data with area information
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )

    # Compute referendum results by regions
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )

    # Display referendum results in a table
    print(referendum_results)

    # Plot the referendum results on a map
    plot_referendum_map(referendum_results)
    plt.show()
