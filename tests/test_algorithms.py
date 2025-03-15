import itertools
import math

import pandas as pd
import pytest

from topk.static import diverse_top_k
from topk.online import online_diverse_selection
import topk.diversity_metrics as diversity_metrics

K = 10  # Number of astronauts to select


# def are_constraints_satisfied(items: tuple[float, any, int], top_k_ids, constraints: dict[any, tuple[float, float]]):
#     k_i = {category: 0 for category in constraints}
#
#     for _, category, id




@pytest.mark.parametrize(
    "algorithm, constraint, has_t",
    [
        (diverse_top_k, diversity_metrics.assign_minimum_diversity, False),
        (diverse_top_k, diversity_metrics.assign_average_diversity, False),
        (diverse_top_k, diversity_metrics.assign_proportion_diversity, False),
        (diverse_top_k, diversity_metrics.assign_relaxed_average_diversity, True),
        (diverse_top_k, diversity_metrics.assign_relaxed_proportion_diversity, True),

        (online_diverse_selection, diversity_metrics.assign_minimum_diversity, False),
        (online_diverse_selection, diversity_metrics.assign_average_diversity, False),
        (online_diverse_selection, diversity_metrics.assign_proportion_diversity, False),
        (online_diverse_selection, diversity_metrics.assign_relaxed_average_diversity, True),
        (online_diverse_selection, diversity_metrics.assign_relaxed_proportion_diversity, True),
    ]
)
def test_static(algorithm, constraint, has_t):
    # Load the dataset
    file_path = "astronauts.csv"  # Update this if needed
    df = pd.read_csv(file_path)

    # Step 1: Process the Data
    # Count the frequency of each undergraduate major
    major_counts = df['Undergraduate Major'].value_counts()

    # Select the top 9 most frequent majors
    top_majors = major_counts.nlargest(9).index.tolist()

    # Create a new category column where less frequent majors are grouped into "Other"
    df['Major Category'] = df['Undergraduate Major'].apply(lambda x: x if x in top_majors else "Other")

    # Extract relevant columns (Score, Category, ID)
    df_filtered = df[['Name', 'Space Flight (hr)', 'Major Category']]

    # Sort the dataset by space flight hours (score) in descending order
    df_filtered = df_filtered.sort_values(by='Space Flight (hr)', ascending=False)

    # Step 2: Define Diversity Constraints (floor = 1, ceil = min(count, 5))
    counts = {category: len(category_df) for category, category_df in df.groupby('Major Category')}
    if has_t:
        diversity_constraints = constraint(K, counts, math.floor(K * .3))
    else:
        diversity_constraints = constraint(K, counts)

    # Convert data into tuple format (score, category, id)
    items = list(zip(df_filtered['Space Flight (hr)'], df_filtered['Major Category'], df_filtered.index))

    # Step 4: Run the Algorithm
    selected_astronauts = algorithm(items, K, diversity_constraints)

    # Step 5: Display Results
    selected_df = df_filtered.iloc[selected_astronauts]
    print("Selected Astronauts:")
    print(selected_df)

