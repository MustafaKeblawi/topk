import math

import pandas as pd
import matplotlib.pyplot as plt

import topk.diversity_metrics
from analyze_static import main as analyze


def prepare_data(K, constraint_algorithm=topk.diversity_metrics.assign_average_diversity, relaxed=False):
    # Load the dataset
    file_path = "datasets/Netflix TV Shows and Movies.csv"  # Update this if needed
    df = pd.read_csv(file_path)

    df["age_certification"] = df["age_certification"].fillna("unmarked")

    df["imdb_score"] = df["imdb_score"].astype(float)

    # Extract relevant columns (Score, Category, ID)
    df_filtered = df[["imdb_score", 'age_certification']]

    # Step 2: Define Diversity Constraints (floor = 1, ceil = min(count, 5))
    counts = {category: len(category_df) for category, category_df in df.groupby('age_certification')}
    if relaxed:
        diversity_constraints = constraint_algorithm(K, counts, K // math.floor(K * .3))
    else:
        diversity_constraints = constraint_algorithm(K, counts)

    # Convert data into tuple format (score, category, id)
    items = list(zip(df_filtered['imdb_score'], df_filtered['age_certification'], df_filtered.index))
    return items, K, diversity_constraints


def main():
    dataset = pd.read_csv("datasets/Netflix TV Shows and Movies.csv")
    filtered_dataframe = pd.DataFrame()
    filtered_dataframe["score"] = dataset["imdb_score"].astype(float)
    filtered_dataframe["age_certification"] = dataset["age_certification"].fillna("unmarked")
    filtered_dataframe.dropna()

    K = 10

    counts = {category: len(category_df) for category, category_df in
              filtered_dataframe.groupby(["age_certification"])}
    items = list(zip(
        filtered_dataframe["score"],
        filtered_dataframe[[col for col in filtered_dataframe.columns if col != "score"]].itertuples(index=False),
        filtered_dataframe.index)
    )

    for i, (a, b, c) in enumerate(items):
        if isinstance(a, str):
            print(i, a)
        # if not isinstance(b, float):
        #     print(i, b)
        if not isinstance(c, int):
            print(i, c)

    analyze(items, K, topk.diversity_metrics.assign_minimum_diversity(K, counts))
    plt.show()


if __name__ == '__main__':
    main()
    # analyze(*prepare_data(K=13))
    # plt.show()
