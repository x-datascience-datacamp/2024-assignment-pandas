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
    """Load data from the CSV files referendum/regions/departments."""

    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv", sep=",")
    departments = pd.read_csv("./data/departments.csv", sep=",")
    
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(
        columns={"region_code": "code_reg", "code": "code_dep", "name": "name_dep"}
    )
    

    merged = departments.merge(regions, on="code_reg", how="left")
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    Drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    referendum_dropped = referendum.copy()

    referendum_dropped['Department code'] = referendum_dropped['Department code'].astype(str)

    referendum_dropped = referendum_dropped[
        referendum_dropped['Department code'].str.match(r'^\d([A-Z0-9])?$')]

    referendum_dropped['code_dep'] = referendum_dropped['Department code'].str.zfill(2)

    regions_and_departments_dropped = regions_and_departments[
        regions_and_departments['code_dep'].str.match(r'^\d[A-Z0-9]$')]

    merged = pd.merge(
        referendum_dropped,
        regions_and_departments_dropped,
        on='code_dep',
        how='left'
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    grouped = referendum_and_areas.groupby(["code_reg", "name_reg"], as_index=False).sum()
    

    result = grouped[
        ["code_reg", "name_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ]
    return result.set_index("code_reg")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    df_info = gpd.read_file('./data/regions.geojson')

    # Merge referendum results geopandas infos
    df_plot = df_info.merge(
        referendum_result_by_regions,
        how='left',
        left_on='code',
        right_on='code_reg'
    )

    # Ration of Choice A compared to all ballots
    df_plot['ratio'] = df_plot['Choice A'] / (df_plot['Choice A']+ df_plot['Choice B'])

    # Plot
    df_plot.plot(column='ratio', legend=True, cmap='viridis')
    plt.title('Referendum Results: Choice A Ratio by Region')
    return df_plot

if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    

    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    

    referendum_and_areas = merge_referendum_and_areas(referendum, regions_and_departments)

    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)
    print(referendum_results)
    

    plot_referendum_map(referendum_results)
    plt.show()
