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
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv", sep=',')
    departments = pd.read_csv("data/departments.csv", sep=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_selected = regions[["code", "name"]]
    departements_selected = departments[["region_code", "code", "name"]]
    merged = pd.merge(regions_selected,
                      departements_selected,
                      left_on='code',
                      right_on='region_code',
                      how='inner')
    merged = merged.rename(columns={
        "code_x": "code_reg",
        "name_x": "name_reg",
        "code_y": "code_dep",
        "name_y": "name_dep"
    })
    merged = merged.drop("region_code", axis=1)
    return merged


def lets_add_a_0(df, column):
    for i in range(len(df)):
        if len(str(df.loc[i, column])) == 1:
            df.loc[i, column] = "0" + str(df.loc[i, column])
    return df


def get_rid_of_str(df, columns, str_todelete):
    return df[~df[columns].str.contains(str_todelete, na=False)]


# Création d'une liste des départements de la France métropolitaine à utiliser
depart_metropol = [i for i in range(1, 97)]
depart_metropol = [str(num) for num in depart_metropol]
pd.DataFrame(depart_metropol, columns=["code_dep"])
for i in range(0, 9):
    depart_metropol[i] = "0" + str(depart_metropol[i])
depart_metropol.append(str("2A"))
depart_metropol.append(str("2B"))


def Metropol_first(df, column):
    return df[df[column].isin(depart_metropol)]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments = Metropol_first(regions_and_departments,
                                             "code_dep")
    referendum = lets_add_a_0(referendum, "Department code")
    referendum = Metropol_first(referendum, "Department code")
    merged_referendum_and_areas = pd.merge(regions_and_departments,
                                           referendum,
                                           left_on="code_dep",
                                           right_on="Department code",
                                           how="outer")
    return merged_referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    merged_gb_data = referendum_and_areas.groupby("name_reg")[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]].sum()
    merged_gb_data = merged_gb_data.reset_index()

    return merged_gb_data


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("data/regions.geojson")
    referendum_result_by_regions_geo = pd.merge(referendum_result_by_regions,
                                                gdf, left_on="name_reg",
                                                right_on="nom")
    referendum_result_by_regions_geo = referendum_result_by_regions_geo.drop(
                                        ["nom", "code"],
                                        axis=1
                                        )
    gdf = gpd.GeoDataFrame(
            referendum_result_by_regions_geo,
            geometry='geometry'
        )
    gdf["ratio"] = (gdf["Choice A"] / (gdf["Choice A"]+gdf["Choice B"]))
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    gdf.plot(column="ratio",
                    legend=True,
                    legend_kwds={'label': "ratio"},
                    ax=ax)
    ax.set_title('A vs rest', fontsize=25)
    ax.axis('off')
    plt.show()
    return gdf


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
