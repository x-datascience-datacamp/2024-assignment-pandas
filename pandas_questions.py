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
    regions = regions.copy()
    departments = departments.copy()
    regions['code'] = regions['code'].astype(str)
    departments['region_code'] = departments['region_code'].astype(str)
    departments['code'] = departments['code'].astype(str).str.zfill(2)
    merged_df = pd.merge(
        regions,
        departments,
        left_on='code',
        right_on='region_code',
        how='inner'
    )
    result = pd.DataFrame({
        'code_reg': merged_df['code_x'],
        'name_reg': merged_df['name_x'],
        'code_dep': merged_df['code_y'],
        'name_dep': merged_df['name_y']
    })
    return result


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum.copy()
    regions_and_departments = regions_and_departments.copy()
    referendum['Department code'] = \
        referendum['Department code'].astype(str).str.zfill(2)
    regions_and_departments['code_dep'] = \
        regions_and_departments['code_dep'].astype(str)
    merged_df = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='inner'
    )
    mainland_codes = (
        set(f"{i:02d}" for i in range(1, 96)) |
        # Corsica
        {'2A', '2B'}
    )
    merged_df = merged_df[merged_df['Department code'].isin(mainland_codes)]
    merged_df = merged_df.dropna()
    required_columns = [
        'Department code', 'Department name', 'Town code', 'Town name',
        'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B',
        'code_dep', 'code_reg', 'name_reg', 'name_dep'
    ]
    return merged_df[required_columns]


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    all_regions = \
        referendum_and_areas[['code_reg', 'name_reg']].drop_duplicates()
    results = referendum_and_areas.groupby(
        ['code_reg', 'name_reg'],
        as_index=False
    ).agg({
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })
    results = pd.merge(
        all_regions,
        results,
        on=['code_reg', 'name_reg'],
        how='outer'
    ).fillna(0)
    results.set_index('code_reg', inplace=True)
    return results[['name_reg', 'Registered', 'Abstentions',
                    'Null', 'Choice A', 'Choice B']]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_data = gpd.read_file('data/regions.geojson')
    merged_geo = geo_data.merge(
        referendum_result_by_regions,
        left_on='code',
        right_index=True,
        how='left'
    )
    merged_geo['ratio'] = (
        merged_geo['Choice A'] /
        (merged_geo['Choice A'] + merged_geo['Choice B'])
    )
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    merged_geo.plot(
        column='ratio',
        ax=ax,
        legend=True,
        legend_kwds={'label': 'Choice A Ratio'},
        cmap='RdYlBu',
        missing_kwds={'color': 'lightgrey'}
    )
    ax.axis('off')
    plt.title('Referendum Results by Region')
    return merged_geo


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
