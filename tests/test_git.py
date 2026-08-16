import subprocess

from analyzer.git import (
    get_changed_files,
    get_commit_changed_files,
    get_commits_after,
)


REPOSITORY = "data/real_repos/flask"
COMMIT = "d8eaaba8"
PARENT_COMMIT = "3596b1ab61ce"


def get_head_commit() -> str:
    """Return the current HEAD commit of the test repository."""

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def test_get_commit_changed_files():
    """Return all files changed by a specific commit."""

    files = get_commit_changed_files(
        REPOSITORY,
        COMMIT,
    )

    assert files == [
        "CHANGES.rst",
        "src/flask/sansio/scaffold.py",
        "tests/test_basic.py",
    ]


def test_get_changed_files():
    """Return files changed between two commits."""

    files = get_changed_files(
        REPOSITORY,
        PARENT_COMMIT,
        COMMIT,
    )

    assert files == [
        "CHANGES.rst",
        "src/flask/sansio/scaffold.py",
        "tests/test_basic.py",
    ]


def test_get_commits_after():
    """Return commits after a given commit in chronological order."""

    commits = get_commits_after(
        REPOSITORY,
        "HEAD~1",
        max_commits=10,
    )

    head = get_head_commit()

    assert commits
    assert commits[-1] == head