import subprocess


def get_change_metrics(
    repository_path: str,
    old_commit: str,
    new_commit: str,
) -> dict[str, dict[str, int]]:
    """
    Calculate line-change metrics for every file changed
    between two Git commits.
    """

    result = subprocess.run(
        [
            "git",
            "diff",
            "--numstat",
            old_commit,
            new_commit,
        ],
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=True,
    )

    metrics = {}

    for line in result.stdout.splitlines():
        parts = line.split("\t")

        if len(parts) != 3:
            continue

        added, deleted, file_path = parts

        # Git uses "-" for binary files.
        if added == "-" or deleted == "-":
            continue

        metrics[file_path] = {
            "lines_added": int(added),
            "lines_deleted": int(deleted),
            "total_changes": int(added) + int(deleted),
        }

    return metrics