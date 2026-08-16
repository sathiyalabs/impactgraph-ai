from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
)


DATASET_PATH = Path("data/flask_dataset_v7.csv")

TARGET_COLUMN = "future_bug_fix_50"

FEATURE_COLUMNS = [
    "lines_added",
    "lines_deleted",
    "total_changes",
    "indirect_impacts",
]


def main():
    print("ImpactGraph AI - Threshold Analysis")
    print("=" * 60)

    df = pd.read_csv(DATASET_PATH)

    split_train = int(len(df) * 0.70)
    split_test = int(len(df) * 0.85)

    train_df = df.iloc[:split_train]
    test_df = df.iloc[split_test:]

    x_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    x_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=5,
    )

    model.fit(x_train, y_train)

    probabilities = model.predict_proba(x_test)[:, 1]

    pr_auc = average_precision_score(
        y_test,
        probabilities,
    )

    print(f"Test rows: {len(test_df)}")
    print(f"Test positives: {int(y_test.sum())}")
    print(f"PR-AUC: {pr_auc:.4f}")

    results = []

    thresholds = [
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
    ]

    for threshold in thresholds:
        predictions = (
            probabilities >= threshold
        ).astype(int)

        precision = precision_score(
            y_test,
            predictions,
            zero_division=0,
        )

        recall = recall_score(
            y_test,
            predictions,
            zero_division=0,
        )

        f1 = f1_score(
            y_test,
            predictions,
            zero_division=0,
        )

        flagged = int(predictions.sum())

        results.append(
            {
                "threshold": threshold,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "flagged": flagged,
            }
        )

    results_df = pd.DataFrame(results)

    print()
    print("=" * 60)
    print("THRESHOLD ANALYSIS")
    print("=" * 60)

    print(
        results_df.to_string(
            index=False,
            float_format=lambda value: f"{value:.4f}",
        )
    )

    best_f1 = results_df.loc[
        results_df["f1"].idxmax()
    ]

    best_precision = results_df.loc[
        results_df["precision"].idxmax()
    ]

    print()
    print("=" * 60)
    print("BEST F1 THRESHOLD")
    print("=" * 60)

    print(
        best_f1.to_string()
    )

    print()
    print("=" * 60)
    print("BEST PRECISION THRESHOLD")
    print("=" * 60)

    print(
        best_precision.to_string()
    )


if __name__ == "__main__":
    main()