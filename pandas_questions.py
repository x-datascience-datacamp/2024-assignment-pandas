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
    referendum = pd.DataFrame(
        pd.read_csv("data/referendum.csv", sep=";", header=0))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv", sep=",", header=0))
    departments = pd.DataFrame(
        pd.read_csv("data/departments.csv", sep=",", header=0))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # il faut merger "region_code" et "code"
    df_merge = pd.merge(
        regions,
        departments,
        left_on="code",
        right_on='region_code')
    df_merge_reg_and_dep = df_merge[
        ['region_code', 'name_x', 'code_y', 'name_y']]
    df_merge_reg_and_dep.rename(columns={
        "region_code": 'code_reg',
        "name_x": 'name_reg',
        "code_y": 'code_dep',
        "name_y": 'name_dep'
    }, inplace=True)
    return pd.DataFrame(df_merge_reg_and_dep)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: f"{int(x):02d}" if str(x).isdigit()
        and 1 <= int(x) <= 9 else x
    )
    df_merge = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on='code_dep')
    dep_list = ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion',
                'Mayotte', 'Saint-Pierre-et-Miquelon', 'Saint-Barthélemy',
                'Saint-Martin', 'Terres australes et antarctiques françaises',
                'Wallis et Futuna', 'Polynésie française',
                'Nouvelle-Calédonie', 'Île de Clipperton']
    df_merge.drop(df_merge[df_merge["name_dep"].isin(dep_list)].index)
    df_merge['Department code'] = df_merge['code_dep']
    return pd.DataFrame(df_merge)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby(by=['code_reg', 'name_reg']).agg({
        "Registered": 'sum',
        "Abstentions": 'sum',
        "Null": 'sum',
        "Choice A": 'sum',
        "Choice B": 'sum'
    }).reset_index()
    df.set_index(
        'code_reg',
        inplace=True)
    return pd.DataFrame(df)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodf = gpd.read_file("data/regions.geojson")
    # referendum_result_by_regions.reset_index(inplace=True)
    gdf_merge = pd.merge(
        referendum_result_by_regions,
        geodf,
        left_on="code_reg",
        right_on='code')
    gdf_merge['ratio'] = (gdf_merge['Choice A'] / (
        gdf_merge['Choice A'] + gdf_merge['Choice B']))
    gdf_merge = gpd.GeoDataFrame(gdf_merge, geometry=gdf_merge["geometry"])
    gdf_merge.plot(
        column='ratio',
        cmap='coolwarm',
        legend=True,
        figsize=(10, 6),
        legend_kwds={"label": "% Ratio Choice A"})

    return gpd.GeoDataFrame(gdf_merge)


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
