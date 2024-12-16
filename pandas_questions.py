import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    departments = pd.read_csv("data/departments.csv", delimiter=',')
    referendum = pd.read_csv("data/referendum.csv", delimiter=';')
    regions = pd.read_csv("data/regions.csv", delimiter=',')

    departments["region_code"] = departments["region_code"].str.lstrip("0")
    regions["code"] = regions["code"].str.lstrip("0")

    print("regions shape", regions.shape)

    return referendum, regions, departments

def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame."""
    # Remove leading zeros
    
    merged = departments.merge(
        regions, left_on="region_code", right_on="code", suffixes=("_dep", "_reg")
    )
    merged = merged.rename(columns={
        "region_code": "code_reg",
        "name": "name_reg",
        "code_dep": "code_dep",
        "name_dep": "name_dep"
    })
    
    merged = merged.loc[:, ~merged.columns.duplicated()]
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments["code_dep"] = regions_and_departments["code_dep"].replace({
        "01": "1", "02": "2", "03": "3", "04": "4", 
        "05": "5", "06": "6", "07": "7", "08": "8", "09": "9"
    })
   
    #referendum = referendum[referendum["Department code"].str.isnumeric()]
    merged = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner"
    )
    return merged

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby(["code_reg", "name_reg"]).sum().reset_index()

    #print(grouped[["code_reg", "name_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]].head())
    grouped = grouped.drop(columns=['code_reg'], axis=1)
    grouped = grouped[[ "name_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]]
    return grouped

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_regions = gpd.read_file("data/regions.geojson")
    geo_regions = geo_regions.rename(columns={"code": "name_reg"})
    print(geo_regions.head())
    print(referendum_result_by_regions.head())

    merged = geo_regions.merge(referendum_result_by_regions, left_on="nom", right_on="name_reg")

    merged["ratio"] = merged["Choice A"] / (merged["Choice A"] + merged["Choice B"])
    
    merged.rename(columns={'nom': 'name_reg'}, inplace=True)

    merged.drop(['name_reg_x'], inplace=True, axis=1)

    merged.plot(column="ratio", legend=True, cmap="coolwarm")
    return merged

if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    print("ref shape", referendum.shape)
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    print("reg dep shape", regions_and_departments.shape)
    referendum_and_areas = merge_referendum_and_areas(referendum, regions_and_departments)
    print("ref and areas ", referendum_and_areas.shape)
    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)


    plot_referendum_map(referendum_results)
    plt.show()
