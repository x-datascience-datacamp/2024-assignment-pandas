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
    referendum = pd.read_csv('../2024-assignment-pandas/data/referendum.csv', sep=';')
    regions = pd.read_csv('../2024-assignment-pandas/data/regions.csv', sep=',')
    departments = pd.read_csv('../2024-assignment-pandas/data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    
    regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'}, inplace=True)
    departments.rename(columns={'region_code': 'code_reg', 'code': 'code_dep', 'name': 'name_dep'}, inplace=True)
    merged = pd.merge(departments, regions, on='code_reg', how='inner')

    return merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    #Normalisation pour le 1 de referendum['Department code'] et le 01 de referendum['Department code'] etc
    referendum['Department code'] = referendum['Department code'].str.zfill(2)

    merged_df = referendum.merge(
        regions_and_departments,
        how='left',
        left_on='Department code',
        right_on='code_dep'
    )

    dom_tom_codes = ['971', '972', '973', '974', '976', '975', '977', '978', 'ZZ']

    merged_df = merged_df[~merged_df['Department code'].isin(dom_tom_codes)]

    # Vérifier les valeurs manquantes
    missing_values_count = merged_df.isnull().sum().sum()
    if missing_values_count > 0:
        merged_df = merged_df.dropna()

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby('name_reg', as_index=False).agg({
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })
    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file('../2024-assignment-pandas/data/regions.geojson')

    merged = gdf.merge(referendum_result_by_regions, left_on='nom', right_on='name_reg', how='left')

    merged['ratio'] = merged['Choice A'] / (merged['Choice A'] + merged['Choice B'])

    ax = merged.plot(column='ratio', legend=True, cmap='viridis', edgecolor='black', figsize=(10, 8))
    ax.set_title('Referendum Results by Region')

    return merged


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
