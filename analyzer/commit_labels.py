import subprocess

from analyzer.labels import classify_commit


def get_commit_subject(
    repository_path: str,
    commit: str,
) -> str:
    """Return the subject line of a Git commit."""

    result = subprocess.run(
        [
            "git",
            "show",
            "-s",
            "--format=%s",
            commit,
        ],
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def find_commit_labels(
    repository_path: str,
    max_commits: int = 50,
) -> list[dict]:
    """
    Classify recent commits.
    """

    commits = get_commit_history(
        repository_path,
        max_commits,
    )

    results = []

    for commit in commits:
        subject = get_commit_subject(
            repository_path,
            commit,
        )

        results.append(
            {
                "commit": commit,
                "subject": subject,
                "label": classify_commit(subject),
            }
        )

    return results