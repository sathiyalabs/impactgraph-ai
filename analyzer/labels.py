import re


STRONG_BUG_KEYWORDS = [
    "regression",
    "crash",
    "broken",
    "incorrect",
    "failure",
    "exception",
    "wrong behavior",
    "wrong output",
    "unexpected behavior",
]


MAINTENANCE_KEYWORDS = [
    "typo",
    "typing",
    "type hint",
    "type hints",
    "type annotation",
    "type annotations",
    "annotation",
    "pyright",
    "mypy",
    "flake8",
    "bugbear",
    "codespell",
    "lint",
    "format",
    "style",
    "documentation",
    "docs",
    "readme",
    "contributing",
    "dependency",
    "dependencies",
    "pip-compile",
    "pre-commit",
    "precommit",
    "workflow",
    "github action",
    "github actions",
    "rtd build",
    "release action",
    "slsa",
]

BUG_FIX_PATTERNS = [
    "fix ",
    "fix:",
    "fixes ",
    "fixed ",
]


def classify_commit(commit_message: str) -> str:
    """
    Classify a commit message into:

    BUG_FIX
    MAINTENANCE_FIX
    OTHER
    """

    message = commit_message.lower().strip()

    # Maintenance/tooling fixes take priority.
    if any(
        keyword in message
        for keyword in MAINTENANCE_KEYWORDS
    ):
        return "MAINTENANCE_FIX"

    # Strong behavioral bug language.
    if any(
        keyword in message
        for keyword in STRONG_BUG_KEYWORDS
    ):
        return "BUG_FIX"

    # Generic "fix" commits.
    if any(
        pattern in message
        for pattern in BUG_FIX_PATTERNS
    ):
        return "BUG_FIX"

    return "OTHER"


def has_issue_reference(commit_message: str) -> bool:
    """
    Detect GitHub-style issue or pull-request references
    such as (#6096).
    """

    return bool(
        re.search(
            r"\(#\d+\)",
            commit_message,
        )
    )


def commit_changes_tests(
    changed_files: list[str],
) -> bool:
    """
    Return True if the commit modifies files that appear
    to be tests.
    """

    return any(
        (
            "/test" in file.replace("\\", "/").lower()
            or file.replace("\\", "/")
            .lower()
            .startswith("test")
            or file.replace("\\", "/")
            .lower()
            .endswith("_test.py")
            or file.replace("\\", "/")
            .lower()
            .endswith("test.py")
        )
        for file in changed_files
    )


BEHAVIOR_CHANGE_KEYWORDS = [
    "settle",
    "correct",
    "properly",
    "incorrect",
    "prevent",
    "avoid",
    "resolve",
    "handle",
    "ensure",
]


def has_behavior_change_language(
    commit_message: str,
) -> bool:
    """
    Detect language suggesting a behavioral correction.
    This is evidence only, not a bug label.
    """

    message = commit_message.lower()

    return any(
        keyword in message
        for keyword in BEHAVIOR_CHANGE_KEYWORDS
    )