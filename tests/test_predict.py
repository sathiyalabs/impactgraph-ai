import pytest

from ml.predict import (
    get_feature_importance,
    get_parent_commit,
    load_model,
    predict_commit,
)


REPOSITORY = "data/real_repos/flask"
COMMIT = "d8eaaba8"


def test_load_model():
    """Load the trained model and its feature definition."""

    model, features = load_model()

    assert model is not None
    assert features

    assert features == [
        "lines_added",
        "lines_deleted",
        "total_changes",
        "direct_impacts",
        "indirect_impacts",
    ]


def test_get_parent_commit():
    """Return the parent commit of a valid commit."""

    parent = get_parent_commit(
        REPOSITORY,
        COMMIT,
    )

    assert len(parent) == 40
    assert parent == "3596b1ab61cea85edb8970e83ff61daa073facf8"


def test_feature_importance_is_ranked():
    """Return model features ordered by descending importance."""

    model, features = load_model()

    ranking = get_feature_importance(
        model,
        features,
    )

    assert len(ranking) == len(features)

    names = [name for name, _ in ranking]
    values = [value for _, value in ranking]

    assert set(names) == set(features)
    assert values == sorted(
        values,
        reverse=True,
    )

    assert all(
        0 <= value <= 1
        for value in values
    )


def test_predict_commit():
    """Run the complete commit-risk prediction pipeline."""

    result = predict_commit(
        REPOSITORY,
        COMMIT,
    )

    assert result["commit"] == COMMIT

    assert len(
        result["old_commit"]
    ) == 40

    assert result["changed_files"]

    assert result["predictions"]

    assert result["risk_level"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    assert 0 <= result["risk_probability"] <= 1

    assert result["feature_importance"]


def test_prediction_records_are_valid():
    """Validate the structure and range of file-level predictions."""

    result = predict_commit(
        REPOSITORY,
        COMMIT,
    )

    changed_files = set(
        result["changed_files"]
    )

    predicted_files = {
        prediction["file"]
        for prediction in result["predictions"]
    }

    assert predicted_files
    assert predicted_files.issubset(
        changed_files
    )

    for prediction in result["predictions"]:
        assert 0 <= prediction["probability"] <= 1

        features = prediction["features"]

        assert features["lines_added"] >= 0
        assert features["lines_deleted"] >= 0
        assert features["total_changes"] >= 0
        assert features["direct_impacts"] >= 0
        assert features["indirect_impacts"] >= 0

        assert (
            features["total_changes"]
            == features["lines_added"]
            + features["lines_deleted"]
        )


def test_overall_probability_matches_highest_prediction():
    """Overall risk should equal the highest file-level probability."""

    result = predict_commit(
        REPOSITORY,
        COMMIT,
    )

    highest_probability = max(
        prediction["probability"]
        for prediction in result["predictions"]
    )

    assert (
        result["risk_probability"]
        == highest_probability
    )


def test_invalid_commit_fails():
    """Reject an invalid Git commit."""

    with pytest.raises(Exception):
        predict_commit(
            REPOSITORY,
            "0000000000000000000000000000000000000000",
        )