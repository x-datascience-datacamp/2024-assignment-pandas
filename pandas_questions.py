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
    referendum = pd.read_csv('data/referendum.csv', sep=";")
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg_and_dep = pd.merge(
        regions, departments, left_on="code", right_on="region_code"
        )
    reg_and_dep = reg_and_dep[["region_code", "name_x", "code_y", "name_y"]]
    reg_and_dep.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return pd.DataFrame(reg_and_dep)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    reg_to_drop = ["COM", "01", "02", "03", "04", "05", "06"]
    reg_and_dep = regions_and_departments[
        ~regions_and_departments["code_reg"].isin(reg_to_drop)
        ]
    ref = referendum[~referendum["Department code"].str.startswith("Z")]
    ref.loc[:, "Department code"] = ref["Department code"].replace(
        {str(i): f"0{i}" for i in range(1, 10)}
        )
    referendum_and_areas = pd.merge(
        reg_and_dep, ref, left_on="code_dep", right_on="Department code"
        )
    return pd.DataFrame(referendum_and_areas)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    votes_by_department = referendum_and_areas.groupby("code_reg")[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
        ].sum().reset_index()
    unique_names = referendum_and_areas[
        ["code_reg", "name_reg"]
        ].drop_duplicates(subset="code_reg")
    votes_by_department = pd.merge(
        votes_by_department, unique_names, on="code_reg", how="inner"
        )
    return pd.DataFrame(votes_by_department[
        ['name_reg', 'Registered', 'Abstentions',
         'Null', 'Choice A', 'Choice B']
        ])


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geographic_data = gpd.read_file("data/regions.geojson")
    ref_by_reg = pd.merge(
        geographic_data, referendum_result_by_regions,
        left_on="nom", right_on="name_reg", how="inner"
        )
    ref_by_reg['ratio'] = ref_by_reg['Choice A'] / (
        ref_by_reg['Choice A'] + ref_by_reg['Choice B']
        )
    ref_by_reg.plot(
        column='ratio', cmap='coolwarm', legend=True,
        figsize=(12, 8), edgecolor='black'
        )
    return gpd.GeoDataFrame(ref_by_reg)


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
