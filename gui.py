import math

import pandas as pd
import streamlit as st

import topk.diversity_metrics

CONSTRAINT_ALGORITHMS: dict[str, tuple[callable, bool]] = {
    "minimum": (topk.diversity_metrics.assign_minimum_diversity, False),
    "proportional": (topk.diversity_metrics.assign_proportion_diversity, False),
    "average": (topk.diversity_metrics.assign_average_diversity, False),
    "relaxed average": (topk.diversity_metrics.assign_relaxed_average_diversity, True),
    "relaxed proportional": (topk.diversity_metrics.assign_relaxed_proportion_diversity, True),
}


def number_input(*args, **kwargs):

    default_toggle = True

    if kwargs.get('max_value') is None:
        default_toggle = False
    if kwargs.get('max_value') is not None and kwargs.get('max_value') > 30:
        default_toggle = False

    if st.toggle("Slider", key=kwargs.get("key") + "_toggle", value=default_toggle):
        return st.slider(*args, **kwargs)
    else:
        return st.number_input(*args, **kwargs)


def dataset_configuration(dataframe: pd.DataFrame, default_score=None, default_sensitives=None):

    if default_sensitives is None:
        default_sensitives = {}

    df_columns = list(dataframe.columns)

    st.selectbox("Score Column", df_columns, key="score_column", index=df_columns.index(default_score))
    st.multiselect("Sensitive Columns", df_columns, key="sensitive_columns", default=default_sensitives)

    column_category_counts = {col: dataframe[col].value_counts() for col in st.session_state.sensitive_columns}

    for sensitive_column in st.session_state.sensitive_columns:
        max_value = len(column_category_counts[sensitive_column])
        if default_sensitives.get(sensitive_column) is not None:
            default_value = default_sensitives.get(sensitive_column)
        else:
            default_value = max_value
        number_input(
            f"N Largest Groups of \"{sensitive_column}\"",
            key=f"n_largest_groups_{sensitive_column}",
            help="Will bin all other groups into \"other\" category.",
            min_value=1,
            max_value=max_value,
            value=default_value,
        )

    selected_n_largest = {col: st.session_state.get(f"n_largest_groups_{col}")
                          for col in st.session_state.sensitive_columns}
    if all(value is not None for value in selected_n_largest.values()):
        top_category_counts = {col: df.nlargest(selected_n_largest[col]) for col, df in column_category_counts.items()}
    filtered_dataframe = pd.DataFrame()
    for sensitive_column in st.session_state.sensitive_columns:
        filtered_dataframe[sensitive_column] = dataframe[sensitive_column].apply(
            lambda x: x if x in top_category_counts[sensitive_column] else "Other")

    filtered_dataframe["score"] = dataframe[st.session_state.score_column]

    counts = {category: len(category_df) for category, category_df in filtered_dataframe.groupby(st.session_state.sensitive_columns)}

    return filtered_dataframe, counts


def app():
    st.write("# TOPK")
    st.write("## Dataset Configuration")
    st.radio("Dataset", ["netflix", "sat", "nasa", "other"], key="dataset", index=2)

    if st.session_state.dataset == "other":
        st.file_uploader("file", type="csv")

    max_K = None

    if st.session_state.dataset == "nasa":
        astronauts = pd.read_csv("astronauts.csv")
        filtered_dataframe, counts = dataset_configuration(
            astronauts,
            default_score="Space Flight (hr)",
            default_sensitives={"Undergraduate Major": 9},
        )
        max_K = len(filtered_dataframe)

    st.write("## Algorithm Configuration")
    if max_K is not None:
        number_input("K", key="K", value=4, step=1, min_value=1, max_value=max_K)
        st.radio("Constraint", CONSTRAINT_ALGORITHMS, key="constraint")

        constraint_algorithm, relaxed = CONSTRAINT_ALGORITHMS[st.session_state.constraint]

        if relaxed:
            number_input("t", key="t", min_value=0.0, value=float(math.floor(st.session_state.K * .3)))
            diversity_constraints = constraint_algorithm(st.session_state.K, counts, st.session_state.t)
        else:
            diversity_constraints = constraint_algorithm(st.session_state.K, counts)

        items = list(zip(
            filtered_dataframe["score"],
            filtered_dataframe[[col for col in filtered_dataframe.columns if col != "score"]].itertuples(index=False),
            filtered_dataframe.index)
        )

        from analyze_static import main
        main(items, st.session_state.K, diversity_constraints)
        st.pyplot()


if __name__ == '__main__':
    app()
