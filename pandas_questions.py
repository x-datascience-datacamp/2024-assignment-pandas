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
    regions = regions.rename(columns={
        "code": "code_reg",
        "name": "name_reg"
    })
    departments = departments.rename(columns={
        "region_code": "code_reg",
        "code": "code_dep",
        "name": "name_dep"
    })
    merged_reg_dep = pd.merge(departments, regions, on="code_reg", how="left")
    merged_reg_dep = merged_reg_dep[["code_reg", "name_reg",
                                     "code_dep", "name_dep"]]
    return merged_reg_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

        You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    """ I get the codes from this link:
      https://fr.wikipedia.org/wiki/France_d%27outre-mer"""
    codes_to_drop = ["971", "972", "973", "974", "975", "976", "977",
                            "978", "986", "987", "988", "989", "984"]
    referendum["Department code"] = (
        referendum["Department code"]
        .astype(str).str.zfill(3))
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"]
        .astype(str).str.zfill(3))
    # Filter DOM-TOM-COM departments and French living abroad
    referendum_updated = (
        referendum[~referendum["Department code"]
                   .isin(codes_to_drop)])
    # Merge referendum with regions and departments
    merged_df = pd.merge(
        referendum_updated,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep", how="inner")
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

        The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }).reset_index()
    grouped.set_index('code_reg', inplace=True)
    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file('data/regions.geojson')
    # print(regions_geo.columns)
    # print(referendum_result_by_regions.columns)
    regions_geo = regions_geo.rename(columns={'code': 'code_reg'})
    merged_db = (
        regions_geo.merge(
            referendum_result_by_regions,
            on='code_reg',
            how='inner'))
    merged_db['ratio'] = (
        merged_db['Choice A'] /
        (
            merged_db['Choice A'] +
            merged_db['Choice B']
        )
            )
    ax = (
        merged_db.plot(
            column='ratio',
            legend=True,
            figsize=(10, 10),
            cmap='coolwarm',
            legend_kwds={
                'label': "Ratio of 'Choice A'",
                'orientation': "horizontal"
                }
                )
        )
    ax.set_title("Referendum Results, Region (Choice A Ratio)", fontsize=15)
    return merged_db


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
