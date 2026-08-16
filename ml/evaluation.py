from pathlib import Path
import json

import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


DATASET = Path("data/flask_dataset_v8.csv")
RESULTS_DIR = Path("results")

TARGET = "future_bug_fix_50"

FULL_FEATURES = [
    "lines_added",
    "lines_deleted",
    "total_changes",
    "direct_impacts",
    "indirect_impacts",
]

CHANGE_FEATURES = [
    "lines_added",
    "lines_deleted",
    "total_changes",
]

THRESHOLD = 0.65


def train_model(x_train, y_train):
    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=5,
    )

    model.fit(x_train, y_train)

    return model


def evaluate_predictions(y_true, probabilities, threshold):
    predictions = (
        probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "pr_auc": float(
            average_precision_score(
                y_true,
                probabilities,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),
        "precision": float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "brier_score": float(
            brier_score_loss(
                y_true,
                probabilities,
            )
        ),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "flagged": int(predictions.sum()),
    }


def main():
    print("ImpactGraph AI - Rigorous Model Evaluation")
    print("=" * 70)

    df = pd.read_csv(DATASET)

    print(f"Dataset rows: {len(df)}")
    print(
        f"Positive samples: "
        f"{int(df[TARGET].sum())}"
    )
    print(
        f"Negative samples: "
        f"{int((df[TARGET] == 0).sum())}"
    )

    # ---------------------------------------------------------
    # Temporal split
    # ---------------------------------------------------------

    split_train = int(len(df) * 0.70)
    split_test = int(len(df) * 0.85)

    train_df = df.iloc[:split_train]
    test_df = df.iloc[split_test:]

    x_train = train_df[FULL_FEATURES]
    y_train = train_df[TARGET]

    x_test = test_df[FULL_FEATURES]
    y_test = test_df[TARGET]

    print()
    print("=" * 70)
    print("TEMPORAL TEST SET")
    print("=" * 70)

    print(f"Training rows: {len(train_df)}")
    print(f"Test rows:     {len(test_df)}")
    print(
        f"Test positives: "
        f"{int(y_test.sum())}"
    )
    print(
        f"Test negatives: "
        f"{int((y_test == 0).sum())}"
    )

    # ---------------------------------------------------------
    # Full dependency-aware model
    # ---------------------------------------------------------

    full_model = train_model(
        x_train,
        y_train,
    )

    full_probabilities = (
        full_model.predict_proba(
            x_test
        )[:, 1]
    )

    full_results = evaluate_predictions(
        y_test,
        full_probabilities,
        THRESHOLD,
    )

    # ---------------------------------------------------------
    # Change-only baseline
    # ---------------------------------------------------------

    baseline_model = train_model(
        train_df[CHANGE_FEATURES],
        y_train,
    )

    baseline_probabilities = (
        baseline_model.predict_proba(
            test_df[CHANGE_FEATURES]
        )[:, 1]
    )

    baseline_results = evaluate_predictions(
        y_test,
        baseline_probabilities,
        THRESHOLD,
    )

    # ---------------------------------------------------------
    # Calibration
    # ---------------------------------------------------------

    calibration_fraction, calibration_mean = (
        calibration_curve(
            y_test,
            full_probabilities,
            n_bins=10,
            strategy="quantile",
        )
    )

    calibration_rows = []

    for predicted, actual in zip(
        calibration_mean,
        calibration_fraction,
    ):
        calibration_rows.append(
            {
                "predicted_probability": float(
                    predicted
                ),
                "observed_frequency": float(
                    actual
                ),
            }
        )

    # ---------------------------------------------------------
    # Print results
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("FULL DEPENDENCY-AWARE MODEL")
    print("=" * 70)

    for key, value in full_results.items():
        if isinstance(value, float):
            print(f"{key:<20}: {value:.4f}")
        else:
            print(f"{key:<20}: {value}")

    print()
    print("=" * 70)
    print("CHANGE-ONLY BASELINE")
    print("=" * 70)

    for key, value in baseline_results.items():
        if isinstance(value, float):
            print(f"{key:<20}: {value:.4f}")
        else:
            print(f"{key:<20}: {value}")

    print()
    print("=" * 70)
    print("MODEL IMPROVEMENT")
    print("=" * 70)

    pr_auc_improvement = (
        full_results["pr_auc"]
        - baseline_results["pr_auc"]
    )

    roc_auc_improvement = (
        full_results["roc_auc"]
        - baseline_results["roc_auc"]
    )

    print(
        f"PR-AUC improvement:  "
        f"{pr_auc_improvement:+.4f}"
    )

    print(
        f"ROC-AUC improvement: "
        f"{roc_auc_improvement:+.4f}"
    )

    print()
    print("=" * 70)
    print("CONFUSION MATRIX")
    print("=" * 70)

    print("                 Predicted")
    print("               Low    High")

    print(
        f"Actual Low   "
        f"{full_results['true_negatives']:5d}"
        f"  {full_results['false_positives']:5d}"
    )

    print(
        f"Actual High  "
        f"{full_results['false_negatives']:5d}"
        f"  {full_results['true_positives']:5d}"
    )

    print()
    print(
        f"Decision threshold: "
        f"{THRESHOLD:.2f}"
    )

    print()
    print("=" * 70)
    print("CALIBRATION")
    print("=" * 70)

    print(
        "Predicted probability -> "
        "Observed frequency"
    )

    for row in calibration_rows:
        print(
            f"{row['predicted_probability']:.4f}"
            f" -> "
            f"{row['observed_frequency']:.4f}"
        )

    print()
    print(
        f"Brier score: "
        f"{full_results['brier_score']:.4f}"
    )

    # ---------------------------------------------------------
    # Save results
    # ---------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = {
        "dataset": str(DATASET),
        "temporal_split": {
            "train_fraction": 0.70,
            "test_start_fraction": 0.85,
        },
        "threshold": THRESHOLD,
        "features": FULL_FEATURES,
        "full_model": full_results,
        "change_only_baseline": baseline_results,
        "improvement": {
            "pr_auc": pr_auc_improvement,
            "roc_auc": roc_auc_improvement,
        },
        "calibration": calibration_rows,
    }

    results_path = RESULTS_DIR / "evaluation.json"

    with results_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )

    calibration_path = (
        RESULTS_DIR / "calibration.csv"
    )

    pd.DataFrame(
        calibration_rows
    ).to_csv(
        calibration_path,
        index=False,
    )

    print()
    print("=" * 70)
    print("RESULTS SAVED")
    print("=" * 70)

    print(
        f"JSON:        {results_path}"
    )

    print(
        f"Calibration: {calibration_path}"
    )


if __name__ == "__main__":
    main()