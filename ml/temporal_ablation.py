from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score


TARGET = "future_bug_fix_50"


FEATURE_GROUPS = {
    "A. Change Only": [
        "lines_added",
        "lines_deleted",
        "total_changes",
    ],
    "B. Change + Direct Impact": [
        "lines_added",
        "lines_deleted",
        "total_changes",
        "direct_impacts",
    ],
    "C. Change + Indirect Impact": [
        "lines_added",
        "lines_deleted",
        "total_changes",
        "indirect_impacts",
    ],
    "D. Change + Direct + Indirect": [
        "lines_added",
        "lines_deleted",
        "total_changes",
        "direct_impacts",
        "indirect_impacts",
    ],
}


DATASETS = {
    "Flask": Path("data/flask_dataset_v8.csv"),
    "Requests": Path("data/requests_dataset_v2.csv"),
    "Click": Path("data/click_dataset_v2.csv"),
}


FOLDS = [
    ("Fold 1", 0.50, 0.65),
    ("Fold 2", 0.60, 0.75),
    ("Fold 3", 0.70, 0.85),
]


def evaluate_fold(
    df: pd.DataFrame,
    train_end: float,
    test_end: float,
    features: list[str],
) -> float:

    train_end_index = int(len(df) * train_end)
    test_end_index = int(len(df) * test_end)

    train_df = df.iloc[:train_end_index]
    test_df = df.iloc[train_end_index:test_end_index]

    x_train = train_df[features]
    y_train = train_df[TARGET]

    x_test = test_df[features]
    y_test = test_df[TARGET]

    if y_train.nunique() < 2:
        return float("nan")

    if y_test.nunique() < 2:
        return float("nan")

    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=5,
    )

    model.fit(x_train, y_train)

    probabilities = model.predict_proba(
        x_test
    )[:, 1]

    return average_precision_score(
        y_test,
        probabilities,
    )


def main():

    print(
        "ImpactGraph AI - Temporal Feature Ablation"
    )
    print("=" * 70)

    results = []

    for repository, dataset_path in DATASETS.items():

        print()
        print("=" * 70)
        print(repository)
        print("=" * 70)

        df = pd.read_csv(dataset_path)

        print(
            f"Dataset rows: {len(df)}"
        )

        for fold_name, train_end, test_end in FOLDS:

            for model_name, features in FEATURE_GROUPS.items():

                pr_auc = evaluate_fold(
                    df,
                    train_end,
                    test_end,
                    features,
                )

                results.append(
                    {
                        "repository": repository,
                        "fold": fold_name,
                        "model": model_name,
                        "pr_auc": pr_auc,
                    }
                )

                print(
                    f"{fold_name:<8} "
                    f"{model_name:<32} "
                    f"PR-AUC: {pr_auc:.4f}"
                )

    results_df = pd.DataFrame(results)

    print()
    print("=" * 70)
    print("TEMPORAL ABLATION SUMMARY")
    print("=" * 70)

    summary = (
        results_df
        .groupby("model")["pr_auc"]
        .agg(
            mean="mean",
            std="std",
            minimum="min",
            maximum="max",
        )
        .sort_values(
            "mean",
            ascending=False,
        )
    )

    print(
        summary.to_string(
            float_format=lambda x:
                f"{x:.4f}",
        )
    )

    print()
    print("=" * 70)
    print("REPOSITORY-LEVEL RESULTS")
    print("=" * 70)

    repository_summary = (
        results_df
        .groupby(
            ["repository", "model"]
        )["pr_auc"]
        .mean()
        .unstack()
    )

    print(
        repository_summary.to_string(
            float_format=lambda x:
                f"{x:.4f}",
        )
    )

    print()
    print("=" * 70)
    print("INDIRECT IMPACT VS CHANGE-ONLY")
    print("=" * 70)

    change = results_df[
        results_df["model"]
        == "A. Change Only"
    ].set_index(
        ["repository", "fold"]
    )["pr_auc"]

    indirect = results_df[
        results_df["model"]
        == "C. Change + Indirect Impact"
    ].set_index(
        ["repository", "fold"]
    )["pr_auc"]

    comparison = pd.DataFrame(
        {
            "change_pr_auc": change,
            "indirect_pr_auc": indirect,
        }
    )

    comparison["improvement"] = (
        comparison["indirect_pr_auc"]
        - comparison["change_pr_auc"]
    )

    print(
        comparison.to_string(
            float_format=lambda x:
                f"{x:.4f}",
        )
    )

    wins = (
        comparison["improvement"] > 0
    ).sum()

    losses = (
        comparison["improvement"] < 0
    ).sum()

    print()
    print(
        f"Indirect impact wins: "
        f"{wins}/{len(comparison)}"
    )

    print(
        f"Indirect impact loses: "
        f"{losses}/{len(comparison)}"
    )

    print(
        f"Mean improvement: "
        f"{comparison['improvement'].mean():+.4f}"
    )


if __name__ == "__main__":
    main()