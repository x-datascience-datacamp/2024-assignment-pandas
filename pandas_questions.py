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
    referendum = pd.read_csv('./data/referendum.csv', sep=";")
    regions = pd.read_csv('./data/regions.csv')
    departments = pd.read_csv('./data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.rename(columns={"name": "name_reg", "code": "code_reg" }, inplace = True)

    departments.rename(columns={"name": "name_dep", "code": "code_dep", 'region_code': 'code_reg'}, inplace = True)

    merged_df = pd.merge(
        regions, departments, on='code_reg',how='right'
    )
    merged_df = merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    # ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    # Department code;Department name;Town code;Town name;Registered;Abstentions;Null;Choice A;Choice B

    referendum_filtered = referendum[~referendum['Department code'].str.startswith(('97', '98', '99'))]

    merged_df = pd.merge(
    referendum_filtered, regions_and_departments,
    left_on='Department code', right_on='code_dep', how='inner'
    )

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    reg_count = referendum_and_areas.groupby(['code_reg', 'name_reg'], as_index=False).agg({
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })

    reg_count.set_index('code_reg', inplace=True)

    

    return reg_count


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geographic_data = gpd.read_file('data/regions.geojson')

    geo_merged = geographic_data.merge(referendum_result_by_regions,
                                         left_on = 'code', right_index =True,
                                         how = 'left' )
    
    geo_merged['ratio'] = geo_merged['Choice A'] / (geo_merged['Choice A'] + geo_merged['Choice B'])

    geo_merged.plot(column='ratio',
                    cmap='Blues',
                    legend=True,
                    legend_kwds = {'label': "Rate of 'Choice A'"},
                    figsize = (10,8),
                    edgecolor = 'black' )
    

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

    print(df_reg.columns, df_dep.columns)

    plot_referendum_map(referendum_results)
    plt.show()
