import csv
from pathlib import Path


FEATURE_COLUMNS = [
    "file",
    "lines_added",
    "lines_deleted",
    "total_changes",
    "direct_impacts",
    "indirect_impacts",
    "total_impacts",
    "old_commit",
    "new_commit",
    "commit_subject",
    "commit_label",
    "evidence_score",
    "evidence_level",
    "future_bug_fix_distance",
    "future_bug_fix_overlap",
    "future_bug_fix_50",
]


def save_features_to_csv(
    features: list[dict],
    output_path: str,
) -> None:
    """Save feature records to a CSV file."""

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FEATURE_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(features)