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
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv")
    departments = pd.read_csv("./data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(
        columns={"code": "code_dep", "name": "name_dep"})

    merged = pd.merge(departments, regions,
                      left_on="region_code", right_on="code_reg")
    final = merged[["code_reg", "name_reg", "code_dep", "name_dep"]]

    return final


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    referendum["Department code"] = referendum["Department code"].replace(
        {
            "1": "01",
            "2": "02",
            "3": "03",
            "4": "04",
            "5": "05",
            "6": "06",
            "7": "07",
            "8": "08",
            "9": "09",
        }
    )

    # List of department codes to exclude (DOM-TOM-COM and
    # French living abroad)
    exclude_codes = [
        "ZA",
        "ZB",
        "ZC",
        "ZD",
        "ZM",
        "ZN",
        "ZP",
        "ZS",
        "ZW",
        "ZX",
        "ZZ",
        "COM",
    ]

    # Filter out unwanted rows from the referendum DataFrame
    referendum_cleaned = referendum[~referendum["Department code"].isin(
        exclude_codes)]

    # Perform the merge
    final = pd.merge(
        referendum_cleaned,
        regions_and_departments,
        how="inner",
        left_on="Department code",
        right_on="code_dep",
    )

    return final


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    regional_results = (
        referendum_and_areas.groupby("code_reg")
        .agg(
            {
                "name_reg": "first",  # Take the first name for the region
                "Registered": "sum",  # Sum the numeric columns
                "Abstentions": "sum",
                "Null": "sum",
                "Choice A": "sum",
                "Choice B": "sum",
            }
        )
        .reset_index()
    )

    # Set 'code_reg' as the index
    regional_results.set_index("code_reg", inplace=True)

    # Reorder columns to match the specified format
    regional_results = regional_results[
        ["name_reg", "Registered", "Abstentions", "Null",
         "Choice A", "Choice B"]
    ]

    return regional_results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("./data/regions.geojson")

    # Step 2: Merge referendum results with
    # geographic data on the region code (code_reg)
    merged = geo_data.merge(
        referendum_result_by_regions, left_on="code",
        right_index=True, how="left"
    )

    # Step 3: Calculate the rate of 'Choice A' over expressed ballots
    # Expressed ballots = Registered - Abstentions - Null
    merged["expressed_ballots"] = (
        merged["Registered"] - merged["Abstentions"] - merged["Null"]
    )
    merged["ratio"] = merged["Choice A"] / merged["expressed_ballots"]

    # Step 4: Plot the map using the 'ratio' column for coloring
    ax = merged.plot(
        column="ratio",
        cmap="coolwarm",
        legend=True,
        figsize=(10, 8),
        legend_kwds={"label": "Rate of 'Choice A'",
                     "orientation": "horizontal"},
    )

    # Optional: Improve plot aesthetics
    ax.set_title("Referendum Results by Region")
    ax.set_axis_off()  # Hide the axis for better visual appeal

    # Show the plot
    plt.show()

    # Step 5: Return the GeoDataFrame with the 'ratio' column
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
