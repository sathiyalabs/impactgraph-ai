from analyzer.metrics import get_change_metrics


REPOSITORY = "data/real_repos/flask"
PARENT_COMMIT = "3596b1ab61ce"
COMMIT = "d8eaaba8"


def test_get_change_metrics():
    """Return line-change metrics for a commit."""

    metrics = get_change_metrics(
        REPOSITORY,
        PARENT_COMMIT,
        COMMIT,
    )

    assert metrics

    scaffold = metrics[
        "src/flask/sansio/scaffold.py"
    ]

    assert scaffold["lines_added"] == 8
    assert scaffold["lines_deleted"] == 0
    assert scaffold["total_changes"] == 8


def test_change_metrics_include_test_file():
    """Include metrics for changed test files."""

    metrics = get_change_metrics(
        REPOSITORY,
        PARENT_COMMIT,
        COMMIT,
    )

    test_file = metrics[
        "tests/test_basic.py"
    ]

    assert test_file["lines_added"] == 5
    assert test_file["lines_deleted"] == 2
    assert test_file["total_changes"] == 7


def test_change_metrics_are_non_negative():
    """All line-change values must be non-negative."""

    metrics = get_change_metrics(
        REPOSITORY,
        PARENT_COMMIT,
        COMMIT,
    )

    for record in metrics.values():
        assert record["lines_added"] >= 0
        assert record["lines_deleted"] >= 0
        assert record["total_changes"] >= 0

        assert (
            record["total_changes"]
            == record["lines_added"]
            + record["lines_deleted"]
        )