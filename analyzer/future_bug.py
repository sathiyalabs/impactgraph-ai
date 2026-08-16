from analyzer.commit_labels import get_commit_subject
from analyzer.git import get_commit_changed_files
from analyzer.labels import classify_commit


def is_strong_bug_fix_commit(
    repository_path: str,
    commit: str,
) -> bool:
    """Return True if the commit is classified as a BUG_FIX."""

    subject = get_commit_subject(
        repository_path,
        commit,
    )

    return classify_commit(subject) == "BUG_FIX"


def build_bug_fix_cache(
    repository_path: str,
    commits: list[str],
) -> dict[str, set[str]]:
    """Cache files changed by BUG_FIX commits."""

    bug_fix_cache = {}

    for commit in commits:

        if not is_strong_bug_fix_commit(
            repository_path,
            commit,
        ):
            continue

        changed_files = get_commit_changed_files(
            repository_path,
            commit,
        )

        if changed_files:
            bug_fix_cache[commit] = set(changed_files)

    return bug_fix_cache


def get_future_bug_fix_distance(
    file_path: str,
    later_commits: list[str],
    bug_fix_cache: dict[str, set[str]],
) -> int:
    """
    Return the number of commits until the next BUG_FIX
    that changes the file.

    Returns 0 if no later BUG_FIX changes the file.
    """

    for distance, commit in enumerate(
        later_commits,
        start=1,
    ):
        changed_files = bug_fix_cache.get(
            commit,
            set(),
        )

        if file_path in changed_files:
            return distance

    return 0


def file_has_future_bug_fix(
    file_path: str,
    later_commits: list[str],
    bug_fix_cache: dict[str, set[str]],
) -> bool:
    """Return True if a later BUG_FIX changes the file."""

    return get_future_bug_fix_distance(
        file_path,
        later_commits,
        bug_fix_cache,
    ) > 0