from pathlib import Path
import subprocess
import sys

import joblib
import pandas as pd

from analyzer.features import build_change_features
from analyzer.git import get_commit_changed_files
from analyzer.graph import build_dependency_graph
from analyzer.metrics import get_change_metrics
from analyzer.repository import temporary_checkout


MODEL_PATH = Path("models/impactgraph_rf.joblib")
FEATURE_PATH = Path("models/features.joblib")


def load_model():
    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURE_PATH)

    return model, features


def get_feature_importance(
    model,
    features,
) -> list[tuple[str, float]]:
    """Return model features ranked by importance."""

    importance = model.feature_importances_

    ranking = sorted(
        zip(features, importance),
        key=lambda item: item[1],
        reverse=True,
    )

    return ranking


def get_parent_commit(
    repository_path: str,
    commit: str,
) -> str:
    """Return the parent commit."""

    result = subprocess.run(
        [
            "git",
            "rev-parse",
            f"{commit}^",
        ],
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def predict_commit(
    repository_path: str,
    commit: str,
) -> dict:
    """Predict future bug-fix risk for a Git commit."""

    model, features = load_model()

    feature_importance = get_feature_importance(
        model,
        features,
    )

    old_commit = get_parent_commit(
        repository_path,
        commit,
    )

    changed_files = get_commit_changed_files(
        repository_path,
        commit,
    )

    if not changed_files:
        raise ValueError(
            "No changed files found for commit."
        )

    change_metrics = get_change_metrics(
        repository_path,
        old_commit,
        commit,
    )

    # Build graph from the parent commit so the
    # current change cannot contaminate the graph.
    with temporary_checkout(
        repository_path,
        old_commit,
    ):
        graph = build_dependency_graph(
            repository_path
        )

        feature_records = build_change_features(
            graph,
            changed_files,
            change_metrics,
        )

    if not feature_records:
        raise ValueError(
            "No changed files could be mapped "
            "to the dependency graph."
        )

    predictions = []

    for record in feature_records:

        row = pd.DataFrame(
            [
                [
                    record[feature]
                    for feature in features
                ]
            ],
            columns=features,
        )

        probability = model.predict_proba(
            row
        )[0, 1]

        predictions.append(
            {
                "file": record["file"],
                "probability": float(
                    probability
                ),
                "features": record,
            }
        )

    max_prediction = max(
        predictions,
        key=lambda x: x["probability"],
    )

    overall_probability = (
        max_prediction["probability"]
    )

    if overall_probability >= 0.75:
        risk_level = "HIGH"
    elif overall_probability >= 0.50:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "commit": commit,
        "old_commit": old_commit,
        "changed_files": changed_files,
        "predictions": predictions,
        "risk_probability": overall_probability,
        "risk_level": risk_level,
        "feature_importance": feature_importance,
    }


def main():

    if len(sys.argv) != 3:
        print("Usage:")
        print(
            "  python -m ml.predict "
            "<repository> <commit>"
        )
        sys.exit(1)

    repository_path = sys.argv[1]
    commit = sys.argv[2]

    result = predict_commit(
        repository_path,
        commit,
    )

    print()
    print("=" * 70)
    print("ImpactGraph AI - Commit Risk Prediction")
    print("=" * 70)

    print(
        f"Commit: {result['commit'][:12]}"
    )

    print(
        f"Parent: {result['old_commit'][:12]}"
    )

    print()
    print(
        f"Files changed: "
        f"{len(result['changed_files'])}"
    )

    print(
        f"Risk probability: "
        f"{result['risk_probability']:.4f}"
    )

    print(
        f"Risk level: "
        f"{result['risk_level']}"
    )

    print()
    print("-" * 70)
    print("FILE-LEVEL PREDICTIONS")
    print("-" * 70)

    for prediction in sorted(
        result["predictions"],
        key=lambda x: x["probability"],
        reverse=True,
    ):

        record = prediction["features"]

        print()
        print(record["file"])

        print(
            f"  Probability: "
            f"{prediction['probability']:.4f}"
        )

        print(
            f"  Added:       "
            f"{record['lines_added']}"
        )

        print(
            f"  Deleted:     "
            f"{record['lines_deleted']}"
        )

        print(
            f"  Total change:"
            f" {record['total_changes']}"
        )

        print(
            f"  Direct:      "
            f"{record['direct_impacts']}"
        )

        print(
            f"  Indirect:    "
            f"{record['indirect_impacts']}"
        )

    print()
    print("-" * 70)
    print("MODEL FEATURE IMPORTANCE")
    print("-" * 70)

    for feature, importance in result[
        "feature_importance"
    ]:
        print(
            f"{feature:<20}"
            f"{importance:.4f}"
        )

    print()
    print("-" * 70)
    print("WHY THIS RISK?")
    print("-" * 70)

    highest_feature, highest_importance = (
        result["feature_importance"][0]
    )

    top_prediction = max(
        result["predictions"],
        key=lambda x: x["probability"],
    )

    top_record = top_prediction["features"]

    print(
        f"  Primary model signal: "
        f"{highest_feature}"
    )

    print(
        f"  Feature importance: "
        f"{highest_importance:.4f}"
    )

    print(
        f"  Code changed: "
        f"{top_record['total_changes']} lines"
    )

    print(
        f"  Direct dependency impact: "
        f"{top_record['direct_impacts']}"
    )

    print(
        f"  Indirect dependency impact: "
        f"{top_record['indirect_impacts']}"
    )

    print(
        f"  Overall predicted risk: "
        f"{result['risk_level']} "
        f"({result['risk_probability']:.2%})"
    )


if __name__ == "__main__":
    main()