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
    referendum = pd.read_csv("./data/referendum.csv", sep = ";")
    regions = pd.read_csv("./data/regions.csv", sep = ",")
    departments = pd.read_csv("./data/departments.csv", sep = ",")

    return referendum, regions, departments

def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    dropped_regions = regions.drop(columns = ['id', 'slug'])
    dropped_departments = departments.drop(columns = ['id', 'slug'])
    dropped_regions = dropped_regions.rename(columns = {'code' : 'code_reg',
                                        'name' : 'name_reg'})
    dropped_departments = dropped_departments.rename(columns = {'code' : 'code_dep',
                                                'name' : 'name_dep',
                                                'region_code' : 'code_reg'})
    regions_and_departments = pd.merge(dropped_departments, dropped_regions, on = 'code_reg', how = 'left')
    
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    dropped_regions_and_departments = regions_and_departments[regions_and_departments['code_reg'] != 'COM']
    dropped_referendum = referendum[~referendum["Department code"].str[0].str.isalpha()]
    dropped_referendum['code_dep'] = dropped_referendum['Department code'].str.zfill(2)
    referendum_and_areas = pd.merge(dropped_referendum, dropped_regions_and_departments, on = 'code_dep', how = 'left')
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    count_by_regions = referendum_and_areas.groupby('name_reg')[['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].sum()
    count_by_regions.reset_index(inplace=True)
    result_by_regions = pd.merge(referendum_and_areas[['code_reg', 'name_reg']], count_by_regions, on='name_reg', how='left') 
    result_by_regions.set_index('code_reg', inplace=True)  
    result_by_regions = result_by_regions.drop_duplicates()
    return result_by_regions

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("./data/regions.geojson")
    referendum_result_by_regions['total_votes'] = referendum_result_by_regions['Registered'] - referendum_result_by_regions['Abstentions'] - referendum_result_by_regions['Null']
    referendum_result_by_regions['ratio'] = referendum_result_by_regions['Choice A'] / referendum_result_by_regions['total_votes']
    map_data = gdf.merge(referendum_result_by_regions, how='left', left_on='code', right_on='code_reg')
    ax = map_data.plot(column='ratio', 
                       cmap='coolwarm', 
                       legend=True, 
                       figsize=(10, 10), 
                       legend_kwds={'label': "Rate of Choice A (%)", 'orientation': "horizontal"})
    ax.set_title('Referendum Results by Region')
    ax.set_axis_off()
    plt.show()
    return map_data


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
