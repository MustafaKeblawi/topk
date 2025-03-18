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

    default_index = None
    if default_score is not None:
        default_index = df_columns.index(default_score)

    st.selectbox("Score Column", df_columns, key="score_column", index=default_index)
    if st.session_state.score_column is None:
        return None
    st.multiselect("Sensitive Columns", [col for col in df_columns if col != st.session_state.score_column], key="sensitive_columns", default=default_sensitives)

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

    max_K = None

    if st.session_state.dataset == "other":
        st.file_uploader("file", type="csv", key="dataset_file")
        try:
            other_dataset = pd.read_csv(st.session_state.dataset_file)
            result = dataset_configuration(other_dataset)
            if result is not None:
                filtered_dataframe, counts = result
                max_K = len(filtered_dataframe)
        except ValueError as e:
            pass


    if st.session_state.dataset == "nasa":
        astronauts = pd.read_csv("astronauts.csv")
        result = dataset_configuration(
            astronauts,
            default_score="Space Flight (hr)",
            default_sensitives={"Undergraduate Major": 9},
        )
        if result is not None:
            filtered_dataframe, counts = result
            max_K = len(filtered_dataframe)

    if st.session_state.dataset == "netflix":
        astronauts = pd.read_csv("datasets/Netflix TV Shows and Movies Binned.csv")
        result = dataset_configuration(
            astronauts,
            default_score="imdb_score",
            default_sensitives={
                "age_certification": 7,
                "release_decade": 7,
            },
        )
        if result is not None:
            filtered_dataframe, counts = result
            max_K = len(filtered_dataframe)

    if st.session_state.dataset == "sat":
        astronauts = pd.read_csv("datasets/scores_backup1.csv")
        result = dataset_configuration(
            astronauts,
            default_score="Average Score (SAT Math)",
            default_sensitives={"City": 10},
        )
        if result is not None:
            filtered_dataframe, counts = result
            max_K = len(filtered_dataframe)


    st.write("## Algorithm Configuration")

    experiment = st.radio("Experiment", ["Warmup Period", "Comparison"])

    if experiment == "Warmup Period":
        if max_K is not None:
            number_input("K", key="K", value=10, step=1, min_value=1, max_value=max_K)
            st.radio("Constraint", CONSTRAINT_ALGORITHMS, key="constraint")


            constraint_algorithm, relaxed = CONSTRAINT_ALGORITHMS[st.session_state.constraint]

            if relaxed:
                number_input("t", key="t", min_value=0, value=math.floor(st.session_state.K * .3))
                diversity_constraints = constraint_algorithm(st.session_state.K, counts, st.session_state.t)
            else:
                diversity_constraints = constraint_algorithm(st.session_state.K, counts)

            items = list(zip(
                filtered_dataframe["score"],
                filtered_dataframe[[col for col in filtered_dataframe.columns if col != "score"]].itertuples(index=False),
                filtered_dataframe.index)
            )

            from analyze_static import main
            fig = main(items, st.session_state.K, diversity_constraints)
            st.pyplot(fig)
    else:
        if max_K is not None:
            number_input("K", key="K", value=4, step=1, min_value=1, max_value=max_K)

            items = list(zip(
                filtered_dataframe["score"],
                filtered_dataframe[[col for col in filtered_dataframe.columns if col != "score"]].itertuples(
                    index=False),
                filtered_dataframe.index)
            )

            constraints_dict = {
                "min": (topk.diversity_metrics.assign_minimum_diversity, False),
                "average": (topk.diversity_metrics.assign_average_diversity, False),
                "proportion": (topk.diversity_metrics.assign_proportion_diversity, False),
                "relaxed_average": (topk.diversity_metrics.assign_relaxed_average_diversity, True),
                "relaxed_proportion": (topk.diversity_metrics.assign_relaxed_proportion_diversity, True),
            }

            inputs = {}
            for constraint_name, (constraint_algorithm, relaxed) in constraints_dict.items():
                if relaxed:
                    diversity_constraints = constraint_algorithm(st.session_state.K, counts,
                                                                 math.floor(st.session_state.K * .3))
                else:
                    diversity_constraints = constraint_algorithm(st.session_state.K, counts)

                items = list(zip(
                    filtered_dataframe["score"],
                    filtered_dataframe[[col for col in filtered_dataframe.columns if col != "score"]].itertuples(
                        index=False),
                    filtered_dataframe.index)
                )

                inputs[constraint_name] = items, st.session_state.K, diversity_constraints

            from analyze_static import main2
            fig = main2(inputs)
            st.pyplot(fig)



if __name__ == '__main__':
    app()
