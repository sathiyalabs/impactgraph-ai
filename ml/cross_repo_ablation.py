from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
)


TARGET_COLUMN = "future_bug_fix_50"

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


def evaluate(
    df: pd.DataFrame,
    features: list[str],
) -> dict:

    split_train = int(len(df) * 0.70)
    split_test = int(len(df) * 0.85)

    train_df = df.iloc[:split_train]
    test_df = df.iloc[split_test:]

    x_train = train_df[features]
    y_train = train_df[TARGET_COLUMN]

    x_test = test_df[features]
    y_test = test_df[TARGET_COLUMN]

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

    predictions = model.predict(
        x_test,
    )

    probabilities = model.predict_proba(
        x_test,
    )[:, 1]

    return {
        "precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "pr_auc": average_precision_score(
            y_test,
            probabilities,
        ),
        "test_rows": len(test_df),
        "test_positives": int(
            y_test.sum()
        ),
    }


def main():

    print(
        "ImpactGraph AI - Cross Repository Ablation"
    )
    print("=" * 70)

    results = []

    for repository, dataset_path in DATASETS.items():

        print()
        print("=" * 70)
        print(repository)
        print("=" * 70)

        if not dataset_path.exists():
            print(
                f"Dataset missing: {dataset_path}"
            )
            continue

        df = pd.read_csv(
            dataset_path
        )

        print(
            f"Dataset rows: {len(df)}"
        )

        change_result = evaluate(
            df,
            CHANGE_FEATURES,
        )

        indirect_result = evaluate(
            df,
            INDIRECT_FEATURES,
        )

        change_pr_auc = (
            change_result["pr_auc"]
        )

        indirect_pr_auc = (
            indirect_result["pr_auc"]
        )

        improvement = (
            indirect_pr_auc
            - change_pr_auc
        )

        relative_improvement = (
            improvement
            / change_pr_auc
            * 100
            if change_pr_auc > 0
            else 0
        )

        print()
        print("Change-only:")

        print(
            f"  Precision: "
            f"{change_result['precision']:.4f}"
        )

        print(
            f"  Recall:    "
            f"{change_result['recall']:.4f}"
        )

        print(
            f"  F1:        "
            f"{change_result['f1']:.4f}"
        )

        print(
            f"  PR-AUC:    "
            f"{change_result['pr_auc']:.4f}"
        )

        print()
        print(
            "Change + Indirect Impact:"
        )

        print(
            f"  Precision: "
            f"{indirect_result['precision']:.4f}"
        )

        print(
            f"  Recall:    "
            f"{indirect_result['recall']:.4f}"
        )

        print(
            f"  F1:        "
            f"{indirect_result['f1']:.4f}"
        )

        print(
            f"  PR-AUC:    "
            f"{indirect_result['pr_auc']:.4f}"
        )

        print()
        print(
            f"PR-AUC improvement: "
            f"{improvement:+.4f}"
        )

        print(
            f"Relative improvement: "
            f"{relative_improvement:+.2f}%"
        )

        results.append(
            {
                "repository": repository,
                "rows": len(df),
                "test_rows": (
                    indirect_result[
                        "test_rows"
                    ]
                ),
                "test_positives": (
                    indirect_result[
                        "test_positives"
                    ]
                ),
                "change_pr_auc": (
                    change_pr_auc
                ),
                "indirect_pr_auc": (
                    indirect_pr_auc
                ),
                "absolute_improvement": (
                    improvement
                ),
                "relative_improvement_%": (
                    relative_improvement
                ),
            }
        )

    print()
    print("=" * 70)
    print(
        "CROSS-REPOSITORY COMPARISON"
    )
    print("=" * 70)

    comparison = pd.DataFrame(
        results
    )

    if comparison.empty:
        print(
            "No datasets available."
        )
        return

    print(
        comparison.to_string(
            index=False,
            float_format=lambda value:
                f"{value:.4f}",
        )
    )

    print()
    print("=" * 70)
    print("AVERAGE")
    print("=" * 70)

    print(
        f"Mean Change-only PR-AUC: "
        f"{comparison['change_pr_auc'].mean():.4f}"
    )

    print(
        f"Mean Indirect-impact PR-AUC: "
        f"{comparison['indirect_pr_auc'].mean():.4f}"
    )

    print(
        f"Mean absolute improvement: "
        f"{comparison['absolute_improvement'].mean():+.4f}"
    )

    print(
        f"Mean relative improvement: "
        f"{comparison['relative_improvement_%'].mean():+.2f}%"
    )


if __name__ == "__main__":
    main()