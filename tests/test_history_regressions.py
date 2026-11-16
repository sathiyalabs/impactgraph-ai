import subprocess

import pytest

from analyzer.generate_dataset import generate_dataset
from analyzer.history import build_history_dataset
from analyzer.repository import temporary_checkout


def git(repository, *args):
    return subprocess.run(
        ["git", *args], cwd=repository, check=True, capture_output=True, text=True
    ).stdout.strip()


def make_repository(path, commits):
    path.mkdir()
    git(path, "init", "-b", "main")
    git(path, "config", "user.name", "Regression Test")
    git(path, "config", "user.email", "test@example.invalid")
    for index in range(commits):
        (path / "app.py").write_text(f"value = {index}\n", encoding="utf-8")
        git(path, "add", "app.py")
        git(path, "commit", "-m", f"Update value {index}")
    return path


def test_default_dataset_includes_complete_future_windows(tmp_path):
    repository = make_repository(tmp_path / "repo", 55)
    dataset = build_history_dataset(str(repository))
    assert len(dataset) == 4
    assert all(record["file"] == "app.py" for record in dataset)
    assert git(repository, "symbolic-ref", "--short", "HEAD") == "main"


def test_insufficient_history_does_not_overwrite_existing_dataset(tmp_path):
    repository = make_repository(tmp_path / "short", 3)
    output = tmp_path / "dataset.csv"
    output.write_text("keep existing dataset\n", encoding="utf-8")
    with pytest.raises(ValueError, match="50-commit future window"):
        generate_dataset(str(repository), str(output))
    assert output.read_text() == "keep existing dataset\n"


def test_checkout_restores_branch_even_after_exception(tmp_path):
    repository = make_repository(tmp_path / "repo", 2)
    head = git(repository, "rev-parse", "HEAD")
    old = git(repository, "rev-parse", "HEAD~1")
    with pytest.raises(RuntimeError):
        with temporary_checkout(str(repository), old):
            assert git(repository, "rev-parse", "HEAD") == old
            raise RuntimeError("analysis failed")
    assert git(repository, "rev-parse", "HEAD") == head
    assert git(repository, "symbolic-ref", "--short", "HEAD") == "main"


def test_checkout_preserves_an_originally_detached_head(tmp_path):
    repository = make_repository(tmp_path / "repo", 2)
    head = git(repository, "rev-parse", "HEAD")
    git(repository, "checkout", "--detach", head)
    with temporary_checkout(str(repository), "HEAD~1"):
        pass
    assert git(repository, "rev-parse", "HEAD") == head
    result = subprocess.run(["git", "symbolic-ref", "--quiet", "HEAD"], cwd=repository)
    assert result.returncode == 1
