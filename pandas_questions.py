"""
Plotting referendum results in pandas.

In short, we want to make a beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
<https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/
blob/main/example_map.png>

To do that, you will load the data as pandas.DataFrame, merge the info, and
aggregate them by regions. Finally, plot them on a map using `geopandas`.
"""


import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    regions = regions.rename(
        columns={'code': 'code_reg', 'name': 'name_reg'}
    )
    departments = departments.rename(
        columns={'code': 'code_dep', 'name': 'name_dep'}
    )
    departments['code_dep'] = departments['code_dep'].astype(
        str
    ).str.zfill(2)
    merged = departments.merge(
        regions,
        left_on='region_code',
        right_on='code_reg',
        how='left'
    )
    merged = merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    referendum['Department code'] = (
        referendum['Department code'].astype(str).str.zfill(2)
    )
    regions_and_departments['code_dep'] = (
        regions_and_departments['code_dep'].astype(str).str.zfill(2)
    )
    merged = referendum.merge(
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='inner'
    )
    merged = merged.dropna()
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    grouped = referendum_and_areas.groupby(
        ['code_reg', 'name_reg'],
        as_index=False
    )[['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].sum()
    grouped = grouped.set_index('code_reg')
    grouped = grouped[
        ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    ]
    return grouped


def plot_referendum_map(referendum_result_by_regions):
    gdf = gpd.read_file('data/regions.geojson')
    gdf_merged = gdf.merge(
        referendum_result_by_regions,
        left_on='nom',
        right_on='name_reg',
        how='left'
    )
    choice_a = gdf_merged['Choice A']
    choice_b = gdf_merged['Choice B']
    total_votes = choice_a + choice_b
    gdf_merged['ratio'] = choice_a / total_votes
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    gdf_merged.plot(
        column='ratio',
        cmap='OrRd',
        linewidth=0.8,
        edgecolor='0.8',
        ax=ax,
        legend=True,
        legend_kwds={
            'label': "Ratio of Choice A Votes",
            'orientation': "horizontal"
        }
    )
    ax.set_title("Referendum Results by Region", fontsize=16, pad=20)
    ax.set_axis_off()
    return gdf_merged


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    gdf_referendum = plot_referendum_map(referendum_results)
    plt.show()

