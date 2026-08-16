import subprocess
from contextlib import contextmanager


def get_current_commit(repository_path: str) -> str:
    """Return the current commit SHA."""

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def checkout_commit(
    repository_path: str,
    commit: str,
) -> None:
    """Checkout a specific commit."""

    subprocess.run(
        ["git", "checkout", "--quiet", commit],
        cwd=repository_path,
        check=True,
    )


def restore_commit(
    repository_path: str,
    commit: str,
) -> None:
    """Restore the repository to the original commit."""

    subprocess.run(
        ["git", "checkout", "--quiet", commit],
        cwd=repository_path,
        check=True,
    )


@contextmanager
def temporary_checkout(
    repository_path: str,
    commit: str,
):
    """
    Temporarily checkout a commit.

    The original commit is restored automatically
    when the context finishes, even if an error occurs.
    """

    original_commit = get_current_commit(repository_path)

    try:
        checkout_commit(repository_path, commit)
        yield
    finally:
        restore_commit(repository_path, original_commit)