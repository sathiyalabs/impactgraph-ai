import re


STRONG_BUG_KEYWORDS = [
    "regression",
    "crash",
    "broken",
    "incorrect",
    "failure",
    "exception",
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

    if any(
        keyword in message
        for keyword in STRONG_BUG_KEYWORDS
    ):
        return "BUG_FIX"

    if any(
        pattern in message
        for pattern in BUG_FIX_PATTERNS
    ):
        maintenance_words = [
            "typo",
            "typing",
            "type",
            "docs",
            "documentation",
            "format",
            "lint",
            "style",
            "dependency",
            "dependencies",
            "test",
        ]

        if any(
            word in message
            for word in maintenance_words
        ):
            return "MAINTENANCE_FIX"

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
def commit_changes_tests(changed_files: list[str]) -> bool:
    """
    Return True if the commit modifies files that appear
    to be tests.
    """

    return any(
        (
            "/test" in file.replace("\\", "/").lower()
            or file.replace("\\", "/").lower().startswith("test")
            or file.replace("\\", "/").lower().endswith("_test.py")
            or file.replace("\\", "/").lower().endswith("test.py")
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
def has_behavior_change_language(commit_message: str) -> bool:
    """
    Detect language suggesting a behavioral correction.
    This is evidence only, not a bug label.
    """

    message = commit_message.lower()

    return any(
        keyword in message
        for keyword in BEHAVIOR_CHANGE_KEYWORDS
    )