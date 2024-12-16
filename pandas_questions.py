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
    #referendum = pd.DataFrame({})
    referendum=pd.read_csv('data/referendum.csv',sep=';')
    regions = pd.read_csv('data/regions.csv',sep=',')
    departments = pd.read_csv('data/departments.csv',sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    temp_rg=regions.rename(columns={'name':'name_reg','code':'code_reg'})
    temp_rg=temp_rg[['name_reg','code_reg']].set_index('code_reg')
    temp_dep=departments.rename(columns={'region_code':'code_reg','name':'name_dep','code':'code_dep'})
    temp_dep=temp_dep[['code_dep','name_dep','code_reg']].set_index('code_reg')
    
    return temp_dep.join(temp_rg).reset_index()


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments=regions_and_departments.set_index('code_dep')
    # formating department code to match code_dep corresponding to metropolitan france departements
    referendum['code_dep']=referendum['Department code'].apply(lambda x : x.zfill(2) if x[0].isnumeric() else 'TODROP')
    temp_ref=referendum.loc[referendum['code_dep']!="TODROP"].set_index('code_dep')
    # joining dataframes
    return temp_ref.join(regions_and_departments).reset_index()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    NumDf=referendum_and_areas[['Registered','Abstentions','Null','Choice A','Choice B','name_reg']]
    NumDf.set_index('name_reg')
    return NumDf.groupby('name_reg').sum().reset_index()


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load geographic data
    geo_data = gpd.read_file('data/regions.geojson')
    geo_data.rename(columns={'nom':'name_reg'}).set_index('name_reg')
    referendum_result_by_regions=referendum_result_by_regions.set_index('name_reg')
    geo_data=referendum_result_by_regions.join(geo_data).reset_index()
    ratio=[geo_data.iloc[i]['Choice A']/ (geo_data.iloc[i]['Choice B']+geo_data.iloc[i]['Choice A']) for i in range(len(geo_data))] 
    geo_data['ratio']=ratio
    geo_data.plot(column='ratio',legend=True,cmap='plasma')
    plt.show()
    return gpd.GeoDataFrame(geo_data)


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
