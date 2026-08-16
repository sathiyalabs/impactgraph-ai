import subprocess
from pathlib import Path


def get_changed_files(
    repository_path: str,
    old_commit: str,
    new_commit: str,
) -> list[str]:
    """
    Return files changed between two Git commits.
    """

    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            old_commit,
            new_commit,
        ],
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def get_commit_changed_files(
    repository_path: str,
    commit: str,
) -> list[str]:
    """
    Return files changed by a single Git commit.
    """

    result = subprocess.run(
        [
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            commit,
        ],
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]
def get_commits_after(
    repository_path: str,
    commit: str,
    max_commits: int = 100,
) -> list[str]:
    """
    Return commits that occurred after the given commit,
    ordered from older to newer.
    """

    result = subprocess.run(
        [
            "git",
            "rev-list",
            "--reverse",
            f"{commit}..HEAD",
            f"-n{max_commits}",
        ],
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]