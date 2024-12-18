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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # regions.code == departments.region_code
    merged_df = pd.merge(
        departments, regions,
        left_on="region_code",  # Match region_code in departments
        right_on="code",        # Match code in regions
        how="left"              # Keep all rows from departments (left join)
    )
    # select the columns and rename them
    result = merged_df[["region_code", "name_y", "code_x", "name_x"]]
    result.columns = ["code_reg", "name_reg", "code_dep", "name_dep"]
    print(result)
    return result


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Drop lines where `code_reg` is "COM/DOM/TOM" from regions_and_departments
    regions_and_departments = regions_and_departments[
        ~regions_and_departments["code_reg"].isin(["COM", "DOM", "TOM"])
        ]
    print(regions_and_departments)
    # Drop another condition
    referendum = referendum[
        referendum["Department name"] != "FRANCAIS DE L'ETRANGER"
        ]

    # Ensure that Department code has leading zeros (e.g., 1 -> 01, 2 -> 02)
    referendum["Department code"] = referendum[
        "Department code"].astype(str).str.zfill(2)

    merged_df = pd.merge(
        referendum, regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="left"
    )

    merged_df = merged_df[
        ['Department code', 'Department name', 'Town code', 'Town name',
         'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B',
         'code_dep', 'code_reg', 'name_reg', 'name_dep']
         ]

    merged_df = merged_df.dropna()

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # group by 'code_reg' and sum the columns
    result = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        # Take the first 'name_reg' in each group
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()

    # Set the region code as the index
    result.set_index('code_reg', inplace=True)

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load geographic data
    geo_data = gpd.read_file('data/regions.geojson')

    # Rename the 'nom' column to 'name'
    geo_data = geo_data.rename(columns={"nom": "name"})

    # Compute ratio for Choice A
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"] /
        (referendum_result_by_regions["Choice A"]
         + referendum_result_by_regions["Choice B"])
    )

    # Merge geographic data with referendum results
    gdf = geo_data.merge(
        referendum_result_by_regions,
        left_on="name",
        right_on="name_reg",
        how="left"
    )

    # Plot the map
    if "ratio" in gdf.columns:
        gdf.plot(
            column="ratio",  # Use the 'ratio' column to color the map
            cmap="viridis",  # Colormap
            legend=True,  # Show legend
            legend_kwds={"label": "Choice A Ratio"}
        )
        plt.title("Referendum Results: Choice A Ratio by Region")
        plt.axis("off")  # Hide axes
    else:
        raise ValueError(
            "'ratio' column not found in the merged GeoDataFrame.")

    # Return the GeoDataFrame
    return gdf


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
