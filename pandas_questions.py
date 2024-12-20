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
    departments = departments.rename(
     columns={
        "code": "code_dep",
        "name": "name_dep"
     }
    )
    merged_df = pd.merge(
     departments,
     regions,
     left_on="region_code",
     right_on="code_reg",
     how="inner"
     )

    final_df = merged_df[["code_reg", "name_reg", "code_dep", "name_dep"]]
    return final_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: '0' + str(x) if len(str(x)) == 1 else str(x)
    )
    referendum = referendum.rename(columns={
        "Department code": "code_dep",
        "Department name": "name_dep"
    })
    merged_df = pd.merge(referendum, regions_and_departments,
                         on="code_dep", how="inner")
    merged_df = merged_df[~merged_df["code_dep"].isin(['COM',
                                                       'DOM', 'TOM', 'ZZ'])]
    merged_df = merged_df.rename(columns={
        "code_dep": "Department code",
        "name_dep_x": "Department name",
        "name_dep_y": "name_dep",
    })
    required_columns = [
        'Department code', 'Department name', 'Town code', 'Town name',
        'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B',
        'code_dep', 'code_reg', 'name_reg', 'name_dep'
    ]
    merged_df['code_dep'] = merged_df['Department code']
    merged_df = merged_df[required_columns]
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped_df = referendum_and_areas.groupby(
     ["code_reg", "name_reg"]
     ).sum(numeric_only=True)

    grouped_df = grouped_df.reset_index()
    result = grouped_df.set_index("code_reg")
    result = result[
     [
        "name_reg",
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B"
        ]
    ]

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file(
        "/Users/mahakhadraoui/2024-assignment-pandas/data/regions.geojson"
        )
    merged_df = geo_data.merge(
        referendum_result_by_regions, how="left",
        right_on="code_reg", left_on="code")
    merged_df["ratio"] = merged_df["Choice A"] / (merged_df["Choice A"]
                                                  + merged_df["Choice B"])
    merged_df.plot(column="ratio", legend=True)
    return merged_df


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
