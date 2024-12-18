import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("referendum.csv", delimiter=";")
    regions = pd.read_csv("regions.csv")
    departments = pd.read_csv("departments.csv")

    return referendum, regions, departments

def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame."""
    merged = pd.merge(
        regions.rename(columns={"code": "code_reg", "name": "name_reg"}),
        departments.rename(columns={"code": "code_dep", "name": "name_dep"}),
        left_on="code_reg",
        right_on="region_code",
        how="inner"  # Use inner join to ensure no missing data
    )
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]

def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame."""
    filtered = referendum[~referendum["Department code"].str.startswith("97")]
    merged = pd.merge(
        filtered,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner"  # Ensure matching records only
    )
    return merged

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region."""
    grouped = referendum_and_areas.groupby(["code_reg", "name_reg"]).sum(numeric_only=True)
    grouped = grouped.rename(
        columns={
            "Registered": "Registered",
            "Abstentions": "Abstentions",
            "Null": "Null",
            "Choice A": "Choice A",
            "Choice B": "Choice B",
        }
    )
    return grouped.reset_index().set_index("code_reg")

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum."""
    geo_data = gpd.read_file("regions.geojson")

    # Calcul du ratio
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"] /
        (
            referendum_result_by_regions["Choice A"] +
            referendum_result_by_regions["Choice B"]
        )
    )

    # Fusion des données géographiques avec les résultats
    merged = geo_data.merge(
        referendum_result_by_regions,
        left_on="code",
        right_on="code_reg",
        how="inner"
    )

    # Affichage de la carte
    merged.plot(column="ratio", legend=True, cmap="coolwarm")
    return merged

if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(referendum, regions_and_departments)
    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
