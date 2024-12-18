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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = departments.merge(
        regions,
        left_on='region_code', 
        right_on='code',       
        suffixes=('_dep', '_reg')
    )
    merged = merged.rename(columns={
        'code_reg': 'code_reg',
        'name_x': 'name_dep',
        'name_y': 'name_reg',
    })
    return merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Filtering out rows with DOM, TOM, COM codes from the 'code_reg' column
    filtered_regions = regions_and_departments[
        ~regions_and_departments['code_reg'].str.contains('DOM|TOM|COM', na=False)
    ].copy()
    
    # Converting 'Department code' and 'code_dep' to consistent formats(AS WE OBSERVE 01,02,03,... DEPT. CODES IN regions_and_departents)
    referendum['Department code'] = referendum['Department code'].astype(str).str.zfill(2)
    filtered_regions['code_dep'] = filtered_regions['code_dep'].astype(str).str.strip()
    
    # Performing the merge between the referendum and regions_and_departments DataFrames
    merged = referendum.merge(
        filtered_regions,
        left_on="Department code",  # Merge on 'Department code' from referendum
        right_on="code_dep",        # Merge on 'code_dep' from regions_and_departments
        how="inner"                 # Use inner join to keep only matching rows
    )

    return merged

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby(['code_reg', 'name_reg']).agg({
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()

    # Ensuring the DataFrame is indexed by 'code_reg'
    grouped = grouped.set_index('code_reg')

    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Loading the geographic data
    regions_geo = gpd.read_file("data/regions.geojson")

    # Calculating the ratio of 'Choice A' over total valid votes
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"] /
        (referendum_result_by_regions["Choice A"] + referendum_result_by_regions["Choice B"])
    )

    # Merging referendum results with geographic data
    geo_merged = regions_geo.merge(
        referendum_result_by_regions,
        left_on="code",      # 'code' in geojson matches 'code_reg'
        right_on="code_reg"
    )

    # Plotting the map
    geo_merged.plot(
        column="ratio",
        cmap="coolwarm",
        legend=True,
        legend_kwds={"label": "Proportion of Choice A"}
    )
    return geo_merged



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
