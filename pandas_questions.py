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
    regions = pd.read_csv("./data/regions.csv", sep=",")
    departments = pd.read_csv("./data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    # Step 1: Rename columns in regions DataFrame
    # - 'code' becomes 'code_reg' (region code)
    # - 'name' becomes 'name_reg' (region name)
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    # Step 2: Rename columns in departments DataFrame
    # - 'region_code' becomes 'code_reg' to align with regions DataFrame
    # - 'code' becomes 'code_dep' (department code)
    # - 'name' becomes 'name_dep' (department name)
    departments = departments.rename(
        columns={"region_code": "code_reg",
                 "code": "code_dep", "name": "name_dep"}
    )

    # Step 3: Merge the departments and regions DataFrames
    # - Perform a left join using 'code_reg' as the key column
    merged_df = pd.merge(departments, regions, on="code_reg", how="left")

    # Step 4: Select the relevant columns for the final output
    merged_df = merged_df[["code_reg", "name_reg", "code_dep", "name_dep"]]

    print(merged_df.head())

    return merged_df
    # return pd.DataFrame({})


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    # Step 1: Filter out rows related to DOM-TOM-COM (Overseas Departments)
    # Department codes starting with '97', '98',
    # '99' are considered overseas departments
    referendum = referendum[
        ~referendum["Department code"].astype(str)
        .str.startswith(("97", "98", "99"))
    ]
    # Step 2: Merge referendum results with regions_and_departments
    # - Use 'Department code' from referendum as the key for the merge
    # - Use 'code_dep' from regions_and_departments as the corresponding key
    merged_df = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )
    # Step 3: Select only the required columns for the final DataFrame
    final_df = merged_df[
        [
            "Department code",
            "Department name",
            "Town code",
            "Town name",
            "Registered",
            "Abstentions",
            "Null",
            "Choice A",
            "Choice B",
            "code_dep",
            "code_reg",
            "name_reg",
            "name_dep",
        ]
    ]
    # Step 4: Print the first few rows for verification
    print(final_df.head())

    # Step 5: Return the cleaned and merged DataFrame
    return final_df
    # return pd.DataFrame({})


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Step 1: Group the data by 'code_reg'
    # and aggregate the values for each region
    result = referendum_and_areas.groupby("code_reg").agg(
        {
            "name_reg": "first",
            "Registered": "sum",
            "Abstentions": "sum",
            "Null": "sum",
            "Choice A": "sum",
            "Choice B": "sum",
        }
    )

    # Step 2: Return the final DataFrame
    return result
    # return pd.DataFrame({})


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Step 1: Load the geographic data
    regions_geo = gpd.read_file("./data/regions.geojson")

    # Step 2: Calculate the ratio for 'Choice A' over total expressed votes
    referendum_result_by_regions["ratio"] = referendum_result_by_regions.apply(
        lambda row: (
            row["Choice A"] / (row["Choice A"] + row["Choice B"])
            if (row["Choice A"] + row["Choice B"]) > 0
            else 0
        ),
        axis=1,
    )

    # Step 3: Merge referendum results with geographic data on 'code_reg'
    merged_geo = regions_geo.merge(
        referendum_result_by_regions,
        left_on="code",  # 'code' dans le fichier geojson
        right_on="code_reg",  # 'code_reg' dans les résultats
        how="left",
    )

    # Step 4: Plot the map using the calculated ratio
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    merged_geo.plot(
        column="ratio",  # Column used for coloring the map
        cmap="Blues",  # Color palette
        linewidth=0.8,
        edgecolor="black",
        legend=True,
        ax=ax,
    )

    plt.title("Référendum : Taux de 'Choice A' par région")
    plt.axis("off")  # Masquer les axes
    plt.show()

    # Step 5: Customize the map
    return merged_geo
    # return gpd.GeoDataFrame({})


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions
    (referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
