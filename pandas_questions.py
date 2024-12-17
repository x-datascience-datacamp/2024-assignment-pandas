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
    """Load data from the CSV files referendum/regions/departments.

    Fix issues related to headers by enforcing proper delimiter
    and stripping spaces.
    """
    # Load data with proper delimiters
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",", header=0)
    departments = pd.read_csv("data/departments.csv", sep=",", header=0)

    # Ensure column names are stripped of leading/trailing spaces
    referendum.columns = referendum.columns.str.strip()
    regions.columns = regions.columns.str.strip()
    departments.columns = departments.columns.str.strip()

    # Print loaded data for debugging
    print("Referendum columns:", referendum.columns)
    print("Regions columns:", regions.columns)
    print("Departments columns:", departments.columns)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments into one DataFrame.

    Columns in the final DataFrame: ['code_reg', 'name_reg',
    'code_dep', 'name_dep'].
    """
    # Rename columns for clarity and to avoid conflicts
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    departments = departments.rename(columns={'code': 'code_dep',
                                              'name': 'name_dep'})

    # Remove duplicates in departments
    departments = departments.drop_duplicates(subset='code_dep')

    # Merge departments with regions on the region_code and code_reg
    merged_df = pd.merge(
        departments,
        regions,
        how='left',
        left_on='region_code',
        right_on='code_reg'
    )

    # Select the required columns
    merged_df = merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    # Debug merged result
    print("Merged regions and departments shape:", merged_df.shape)
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum data with regions_and_departments."""
    # Ensure data types match
    referendum['Department code'] = referendum['Department code'].astype(str)
    regions_and_departments['code_dep'] = regions_and_departments['code_dep'] \
        .astype(str)

    # Remove duplicates in regions_and_departments
    regions_and_departments = regions_and_departments.drop_duplicates(
        subset=['code_dep']
    )

    # Merge the data
    merged = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='left'
    )

    # Fill missing values
    merged = merged.fillna(0)

    # Debugging: print shape and columns
    print("Shape of merged DataFrame:", merged.shape)
    print("Columns in merged DataFrame:", merged.columns)
    print("Sample rows:\n", merged.head())

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Aggregate referendum results by regions."""
    # Drop invalid or missing regions
    referendum_and_areas = referendum_and_areas[
        referendum_and_areas['code_reg'] != 0
    ]
    referendum_and_areas = referendum_and_areas.dropna(subset=['code_reg'])

    # Debug input shape and total before aggregation
    print("Shape before aggregation:", referendum_and_areas.shape)
    print(
        "Total Registered before aggregation:",
        referendum_and_areas['Registered'].sum()
    )

    # Group data by region and sum all numerical columns
    aggregated = referendum_and_areas.groupby(
        ['code_reg', 'name_reg'],
        as_index=False
    ).sum()

    # Debug aggregated totals
    print("Aggregated shape:", aggregated.shape)
    print(
        "Total Registered after aggregation:",
        aggregated['Registered'].sum()
    )

    return aggregated.set_index('code_reg')[
        [
            'name_reg', 'Registered', 'Abstentions',
            'Null', 'Choice A', 'Choice B'
        ]
    ]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with referendum results.

    Loads geographic data and merges it with referendum
    results. Computes and displays
    the rate of 'Choice A' over all expressed ballots.
    """
    # Load geographic data
    regions_geo = gpd.read_file("data/regions.geojson")

    # Calculate the ratio of Choice A
    referendum_result_by_regions = referendum_result_by_regions.copy()
    referendum_result_by_regions['ratio'] = (
        referendum_result_by_regions['Choice A'] /
        (
            referendum_result_by_regions['Choice A'] +
            referendum_result_by_regions['Choice B']
        )
    )

    # Merge geographic data with referendum results
    merged_geo = regions_geo.merge(
        referendum_result_by_regions,
        left_on='code',
        right_index=True
    )

    # Plot the map
    merged_geo.plot(
        column='ratio',
        cmap='viridis',
        legend=True,
        legend_kwds={
            'label': "Ratio of Choice A",
            'orientation': "horizontal"
        }
    )

    plt.title("Referendum Results: Ratio of Choice A")
    return merged_geo


if __name__ == "__main__":
    referendum, regions, departments = load_data()
    regions_and_departments = merge_regions_and_departments(
            regions,
            departments
        )
    referendum_and_areas = merge_referendum_and_areas(
            referendum,
            regions_and_departments
        )
    referendum_results = compute_referendum_result_by_regions(
            referendum_and_areas
        )
    print("Final referendum results:\n", referendum_results)
    plot_referendum_map(referendum_results)
    plt.show()
