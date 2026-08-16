from analyzer.labels import (
    classify_commit,
    has_issue_reference,
    commit_changes_tests,
    has_behavior_change_language,
)


def calculate_evidence_score(
    commit_message: str,
    changed_files: list[str],
) -> int:
    """
    Calculate a transparent bug-evidence score.

    This is a heuristic, NOT ground truth.
    """

    label = classify_commit(commit_message)

    score = 0

    # Strong bug language.
    if label == "BUG_FIX":
        score += 3

    # Issue / PR reference.
    if has_issue_reference(commit_message):
        score += 1

    # Tests changed.
    if commit_changes_tests(changed_files):
        score += 1

    # Behavioral correction language.
    if has_behavior_change_language(commit_message):
        score += 1

    # Maintenance changes reduce confidence.
    if label == "MAINTENANCE_FIX":
        score -= 3

    return max(0, score)


def get_evidence_level(score: int) -> str:
    """Convert evidence score into a confidence level."""

    if score >= 4:
        return "HIGH"

    if score >= 2:
        return "MEDIUM"

    return "LOW"