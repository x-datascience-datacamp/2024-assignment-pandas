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
    df = pd.merge(
        regions, departments,
        left_on="code",
        right_on="region_code",
        how="inner")

    df = df.rename(
        columns={
            "code_x": "code_reg",
            "name_x": "name_reg",
            "code_y": "code_dep",
            "name_y": "name_dep",
        })

    df = df.drop(columns=["id_x", "id_y", "region_code", "slug_x", "slug_y"])

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Drop lines relative to DOM-TOM-COM and french living abroad
    df1 = referendum[~referendum["Department name"].str.contains(
        "FRANCAIS DE L\'ETRANGER", na=False)]
    df1 = df1[~df1["Department code"].str.contains("Z", na=False)]

    # Adjust code_dep
    df1["Department code"] = df1["Department code"].apply(
        lambda x: "0" + x if len(x) == 1 else x)

    # Consider code_dep as str
    df1["Department code"] = df1["Department code"].astype(str)
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].astype(str))

    # Merge
    df = pd.merge(
        df1,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="left")

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped_df = (
        referendum_and_areas.groupby(['code_reg', 'name_reg'], as_index=False)
        .sum(numeric_only=True))

    grouped_df = grouped_df.set_index("code_reg")
    columns = ['name_reg',
               'Registered',
               'Abstentions',
               'Null',
               'Choice A',
               'Choice B']

    grouped_df = grouped_df[columns]

    return grouped_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    df_info = gpd.read_file('data/regions.geojson')

    # Merge referendum results geopandas infos
    df_plot = df_info.merge(
        referendum_result_by_regions,
        how='left',
        left_on='code',
        right_on='code_reg'
    )

    # Ration of Choice A compared to all ballots
    df_plot['ratio'] = df_plot['Choice A'] / (df_plot['Choice A']
                                              + df_plot['Choice B'])

    # Plot
    df_plot.plot(column='ratio', legend=True, cmap='viridis')
    plt.title('Referendum Results: Choice A Ratio by Region')

    return df_plot


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
