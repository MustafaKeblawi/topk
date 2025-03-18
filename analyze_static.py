import pandas as pd

from topk.static import diverse_top_k
from topk.online import online_diverse_selection
import topk.diversity_metrics
import numpy as np
import matplotlib.pyplot as plt
import math
import random

random.seed(0)


def prepare_data(K, constraint_algorithm=topk.diversity_metrics.assign_average_diversity, relaxed=False):
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

    # Step 2: Define Diversity Constraints (floor = 1, ceil = min(count, 5))
    counts = {category: len(category_df) for category, category_df in df.groupby('Major Category')}
    if relaxed:
        diversity_constraints = constraint_algorithm(K, counts, K // math.floor(K * .3))
    else:
        diversity_constraints = constraint_algorithm(K, counts)

    # Convert data into tuple format (score, category, id)
    items = list(zip(df_filtered['Space Flight (hr)'], df_filtered['Major Category'], df_filtered.index))
    return items, K, diversity_constraints


def calc_accuracy(min_val, optimal_sol, sub_optimal):
    sum1 = 0
    sum2 = 0
    for i in range(len(optimal_sol)):
        sum2 += (optimal_sol[i] - min_val)
        sum1 += (sub_optimal[i] - min_val)
    return sum1 / sum2


def main(items, K, diversity_constraints):
    print(diversity_constraints)
    items.sort(reverse=True, key=lambda x: x[0])
    items_dict = {id_: (score, category) for score, category, id_ in items}
    print(len(items))

    # Define warm-up factors
    warmup_factors = [1, 0.25, 1 / 16]  # Full (N/e), 1/4 (N/4e), 1/16 (N/16e)
    warmup_labels = ["Full (N/e)", "1/4 (N/4e)", "1/16 (N/16e)"]
    optimal_solution = diverse_top_k(items, K, diversity_constraints)
    optimal_scores = [items_dict[i][0] for i in optimal_solution]
    optimal_solution.sort()
    min_val = min([score for score, _, _ in items])
    # Store results
    accuracy_results = []
    walking_distance_results = []

    for factor in warmup_factors:
        walking_distance_factor = []
        accuracy_factor = []
        for run in range(100):
            random.shuffle(items)
            selected, walking_distance = online_diverse_selection(items, K, diversity_constraints, factor)
            if len(selected) < K:
                continue
            scores = [items_dict[i][0] for i in selected]
            accuracy_factor.append(calc_accuracy(min_val, optimal_scores, scores))
            if accuracy_factor[-1] > 1.0:
                print(run)
            walking_distance_factor.append(walking_distance)
        accuracy_results.append(accuracy_factor)
        walking_distance_results.append(walking_distance_factor)

    # Step 7: Generate three separate graphs for each warm-up strategy
    # Assuming walking_distance_results and accuracy_results are available from previous computations

    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    for i in range(3):
        x_data = np.array(walking_distance_results[i])  # X-axis: Walking distance
        y_data = np.array(accuracy_results[i])  # Y-axis: Accuracy

        # Scatter plot
        axs[i].scatter(x_data, y_data, color='blue', s=10, alpha=0.6, label="Data Points")

        # Fit a trend line (linear regression)
        if len(x_data) > 1:  # Ensure enough data points to fit a line
            coef = np.polyfit(x_data, y_data, 1)  # 1st-degree polynomial (linear)
            poly1d_fn = np.poly1d(coef)  # Create function from coefficients

            # Plot trend line
            x_range = np.linspace(min(x_data), max(x_data), 100)  # Generate X values for trend line
            axs[i].plot(x_range, poly1d_fn(x_range), color='red', linestyle="-", label="Trend Line")

        # Formatting
        right_max = None
        for l in  walking_distance_results:
            if l:
                right_max = max(l)
        if right_max is not None:
            right_max = math.ceil(1.1*right_max)
        axs[i].set_xlim(left=0, right=right_max)  # Ensures x-axis starts from 0
        axs[i].set_ylim(bottom=0, top=1.1)  # Ensures y-axis starts from 0
        axs[i].set_xlabel("Walking Distance (Number of Items Examined)")
        axs[i].set_ylabel("Accuracy (Selected Score / Best Possible Score)")
        axs[i].set_title(f"Warm-Up Strategy: {warmup_labels[i]}")
        axs[i].grid(True)
        axs[i].legend()  # Show legend

    return fig
    # plt.tight_layout()
    # plt.show()


def main2(inputs: dict[str, tuple[any, any, any]]):
    constaint_results={}
    for constraint_name, (items, K, diversity_constraints) in inputs.items():
        items.sort(reverse=True)
        items_dict = {id_: (score, category) for score, category, id_ in items}
        optimal_solution = diverse_top_k(items, K, diversity_constraints)
        optimal_scores = [items_dict[i][0] for i in optimal_solution]
        min_val = min([score for score, _, _ in items])
        accuracies = []
        walking_distances = []
        for i in range(100):
            random.shuffle(items)
            selected, walking_distance = online_diverse_selection(items, K, diversity_constraints)
            scores = [items_dict[i][0] for i in selected]
            accuracies.append(calc_accuracy(min_val, optimal_scores, scores))
            walking_distances.append(walking_distance)
        constaint_results[constraint_name]=(accuracies,walking_distances)
    import matplotlib.pyplot as plt

    # Assuming `constaint_results` is already populated with accuracies and walking distances for each constraint
    fig, ax = plt.subplots(figsize=(10, 6))

    # Loop through each constraint and plot its results
    for constraint_name, (accuracies, walking_distances) in constaint_results.items():
        ax.scatter(walking_distances, accuracies, label=constraint_name, s=10, alpha=0.6)

        # Fit a trend line for each constraint (linear regression)
        if len(walking_distances) > 1:
            coef = np.polyfit(walking_distances, accuracies, 1)  # Linear regression
            poly1d_fn = np.poly1d(coef)  # Create function from coefficients

            # Generate X values for trend line
            x_range = np.linspace(min(walking_distances), max(walking_distances), 100)
            ax.plot(x_range, poly1d_fn(x_range), linestyle="--")

    # Formatting
    ax.set_xlabel("Walking Distance (Number of Items Examined)")
    ax.set_ylabel("Accuracy (Selected Score / Best Possible Score)")
    ax.set_title("Accuracy vs. Walking Distance for Different Constraints")
    ax.legend()  # Show legend for constraint names
    ax.grid(True)

    return fig


if __name__ == '__main__':
    main(*prepare_data(K=40))
    plt.show()
    # main2()
