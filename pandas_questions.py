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
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.
    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    reg = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    dep = departments.rename(columns={'code': 'code_dep', 'name': 'name_dep',
                                      'region_code': 'code_reg'})
    reg_dep = pd.merge(dep.loc[:, ['code_dep', 'name_dep', 'code_reg']],
                       reg.loc[:, ['code_reg', 'name_reg']], on='code_reg')

    return reg_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    code_to_del = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN',
                   'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']

    ref = referendum[~referendum['Department code'].isin(code_to_del)]

    ref['Department code'][(ref['Department code'] != '2A') &
                           (ref['Department code'] != '2B')] = (
        ref['Department code'][(ref['Department code'] != '2A') &
                               (ref['Department code'] != '2B')].astype(int)
    )
    regions_and_departments['code_dep'][
        (regions_and_departments['code_dep'] != '2A') &
        (regions_and_departments['code_dep'] != '2B')
    ] = regions_and_departments['code_dep'][
        (regions_and_departments['code_dep'] != '2A') &
        (regions_and_departments['code_dep'] != '2B')
    ].astype(int)

    fusion_ref_reg_dep = pd.merge(
        ref, regions_and_departments,
        right_on='code_dep', left_on='Department code'
    )

    return fusion_ref_reg_dep


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.set_index('code_reg')
    res_by_regions = referendum_and_areas.loc[
        :, ['name_reg', 'Registered', 'Abstentions', 'Null',
            'Choice A', 'Choice B']
    ].groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })
    return res_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file('data/regions.geojson')
    gdf = gdf.rename(columns={'nom': 'name_reg'})
    res = gdf.merge(referendum_result_by_regions, on='name_reg')
    res['ratio'] = res['Choice A'] / (res['Choice A'] +
                                      res['Choice B'])
    res.plot(column='ratio', legend=True)

    print(res)
    return res


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
