from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score


TARGET = "future_bug_fix_50"

CHANGE_FEATURES = [
    "lines_added",
    "lines_deleted",
    "total_changes",
]

INDIRECT_FEATURES = [
    "lines_added",
    "lines_deleted",
    "total_changes",
    "indirect_impacts",
]

DATASETS = {
    "Flask": Path("data/flask_dataset_v8.csv"),
    "Requests": Path("data/requests_dataset_v2.csv"),
    "Click": Path("data/click_dataset_v2.csv"),
}


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

    model.fit(
        x_train,
        y_train,
    )

    probabilities = model.predict_proba(
        x_test
    )[:, 1]

    return average_precision_score(
        y_test,
        probabilities,
    )


def main():

    print(
        "ImpactGraph AI - Temporal Validation"
    )
    print("=" * 70)

    all_results = []

    folds = [
        ("Fold 1", 0.50, 0.65),
        ("Fold 2", 0.60, 0.75),
        ("Fold 3", 0.70, 0.85),
    ]

    for repository, dataset_path in DATASETS.items():

        print()
        print("=" * 70)
        print(repository)
        print("=" * 70)

        df = pd.read_csv(dataset_path)

        print(
            f"Dataset rows: {len(df)}"
        )

        for fold_name, train_end, test_end in folds:

            change_pr_auc = evaluate_fold(
                df,
                train_end,
                test_end,
                CHANGE_FEATURES,
            )

            indirect_pr_auc = evaluate_fold(
                df,
                train_end,
                test_end,
                INDIRECT_FEATURES,
            )

            improvement = (
                indirect_pr_auc
                - change_pr_auc
            )

            print()
            print(f"{fold_name}")
            print("-" * 40)

            print(
                f"Change-only PR-AUC: "
                f"{change_pr_auc:.4f}"
            )

            print(
                f"Indirect-impact PR-AUC: "
                f"{indirect_pr_auc:.4f}"
            )

            print(
                f"Improvement: "
                f"{improvement:+.4f}"
            )

            all_results.append(
                {
                    "repository": repository,
                    "fold": fold_name,
                    "change_pr_auc": change_pr_auc,
                    "indirect_pr_auc": indirect_pr_auc,
                    "improvement": improvement,
                }
            )

    results = pd.DataFrame(
        all_results
    )

    print()
    print("=" * 70)
    print("TEMPORAL VALIDATION SUMMARY")
    print("=" * 70)

    print(
        results.to_string(
            index=False,
            float_format=lambda x:
                f"{x:.4f}",
        )
    )

    print()
    print("=" * 70)
    print("REPOSITORY AVERAGES")
    print("=" * 70)

    repository_summary = (
        results
        .groupby("repository")
        [
            [
                "change_pr_auc",
                "indirect_pr_auc",
                "improvement",
            ]
        ]
        .mean()
    )

    print(
        repository_summary.to_string(
            float_format=lambda x:
                f"{x:.4f}",
        )
    )

    print()
    print("=" * 70)
    print("OVERALL")
    print("=" * 70)

    print(
        f"Mean Change-only PR-AUC: "
        f"{results['change_pr_auc'].mean():.4f}"
    )

    print(
        f"Mean Indirect-impact PR-AUC: "
        f"{results['indirect_pr_auc'].mean():.4f}"
    )

    print(
        f"Mean improvement: "
        f"{results['improvement'].mean():+.4f}"
    )


if __name__ == "__main__":
    main()