from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path("models/impactgraph_rf.joblib")
FEATURE_PATH = Path("models/features.joblib")


def load_model():
    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURE_PATH)

    return model, features


def predict_risk(
    lines_added: int,
    lines_deleted: int,
    total_changes: int,
    direct_impacts: int,
    indirect_impacts: int,
) -> dict:

    model, features = load_model()

    values = {
        "lines_added": lines_added,
        "lines_deleted": lines_deleted,
        "total_changes": total_changes,
        "direct_impacts": direct_impacts,
        "indirect_impacts": indirect_impacts,
    }

    row = pd.DataFrame(
        [[values[feature] for feature in features]],
        columns=features,
    )

    probability = model.predict_proba(
        row
    )[0, 1]

    if probability >= 0.75:
        risk_level = "HIGH"
    elif probability >= 0.50:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_probability": float(probability),
        "risk_level": risk_level,
        "features": values,
    }


def main():

    result = predict_risk(
        lines_added=20,
        lines_deleted=5,
        total_changes=25,
        direct_impacts=2,
        indirect_impacts=8,
    )

    print("ImpactGraph AI - Risk Prediction")
    print("=" * 50)

    print(
        f"Risk probability: "
        f"{result['risk_probability']:.4f}"
    )

    print(
        f"Risk level: "
        f"{result['risk_level']}"
    )

    print()
    print("Features:")

    for name, value in result["features"].items():
        print(
            f"  {name}: {value}"
        )


if __name__ == "__main__":
    main()