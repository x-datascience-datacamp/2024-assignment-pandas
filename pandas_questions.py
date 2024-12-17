import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    # load the referendum data
    referendum = pd.read_csv('data/referendum.csv', sep=';')

    # load the regions data
    regions = pd.read_csv('data/regions.csv')

    # load the departments data
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # merge the regions and departments on the region code
    merged = pd.merge(regions, departments, left_on='code',
                      right_on='region_code', how='left')
    merged.columns = ['id_reg', 'code_reg', 'name_reg', 'slug_reg', 'id_dep',
                      'region_code', 'code_dep', 'name_dep', 'slug_dep']
    return merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum[~referendum["Department code"].str.startswith('Z')]
    regions_and_departments["code_dep"] = regions_and_departments["code_dep"] \
        .str.lstrip('0')
    merged = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="left"
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    selected_columns = ['name_reg', 'Registered', 'Abstentions',
                        'Null', 'Choice A', 'Choice B']
    groupby_code_reg = referendum_and_areas.groupby("code_reg")
    agregg = groupby_code_reg.agg({'name_reg': 'first',
                                   'Registered': 'sum',
                                   'Abstentions': 'sum',
                                   'Null': 'sum',
                                   'Choice A': 'sum',
                                   'Choice B': 'sum'})
    agregg = agregg[selected_columns]
    return agregg


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodata = gpd.read_file("./data/regions.geojson")
    referendum_result_by_regions["code"] = referendum_result_by_regions.index
    merged = pd.merge(geodata, referendum_result_by_regions)
    all_expressed = merged["Choice A"] + merged["Choice B"]
    merged['ratio'] = merged['Choice A'] / all_expressed
    merged = gpd.GeoDataFrame(merged)
    merged.plot(column="ratio")
    plt.show()
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
