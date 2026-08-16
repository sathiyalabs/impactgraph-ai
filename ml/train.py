from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


DATASET = Path("data/flask_dataset_v8.csv")
MODEL_DIR = Path("models")

MODEL_PATH = MODEL_DIR / "impactgraph_rf.joblib"
FEATURE_PATH = MODEL_DIR / "features.joblib"

TARGET = "future_bug_fix_50"

FEATURES = [
    "lines_added",
    "lines_deleted",
    "total_changes",
    "direct_impacts",
    "indirect_impacts",
]


def main():
    print("ImpactGraph AI - Model Training")
    print("=" * 60)

    df = pd.read_csv(DATASET)

    print(f"Dataset rows: {len(df)}")
    print(f"Positive samples: {df[TARGET].sum()}")
    print(f"Negative samples: {(df[TARGET] == 0).sum()}")

    x = df[FEATURES]
    y = df[TARGET]

    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=5,
    )

    model.fit(x, y)

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    joblib.dump(
        FEATURES,
        FEATURE_PATH,
    )

    print()
    print("Training complete.")
    print(f"Model saved: {MODEL_PATH}")
    print(f"Features saved: {FEATURE_PATH}")


if __name__ == "__main__":
    main()