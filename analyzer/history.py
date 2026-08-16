from pathlib import Path
import subprocess

from analyzer.commit_labels import get_commit_subject
from analyzer.evidence import (
    calculate_evidence_score,
    get_evidence_level,
)
from analyzer.features import build_change_features
from analyzer.future_bug import (
    build_bug_fix_cache,
    get_future_bug_fix_distance,
)
from analyzer.git import get_changed_files
from analyzer.graph import build_dependency_graph
from analyzer.labels import classify_commit
from analyzer.metrics import get_change_metrics
from analyzer.repository import temporary_checkout


def get_commit_history(
    repository_path: str,
    max_commits: int = 20,
) -> list[str]:
    """Return recent commit hashes."""

    result = subprocess.run(
        [
            "git",
            "log",
            "--format=%H",
            f"-n{max_commits}",
        ],
        cwd=repository_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    return [
        commit.strip()
        for commit in result.stdout.splitlines()
        if commit.strip()
    ]


def create_commit_pairs(
    commits: list[str],
) -> list[tuple[str, str]]:
    """Create chronological commit pairs."""

    chronological_commits = list(reversed(commits))

    return [
        (
            chronological_commits[index],
            chronological_commits[index + 1],
        )
        for index in range(len(chronological_commits) - 1)
    ]


def build_history_dataset(
    repository_path: str,
    max_commits: int = 20,
) -> list[dict]:
    """
    Build historical feature records.

    Includes:
    - change metrics
    - dependency impacts
    - commit classification
    - evidence score
    - future bug-fix distance
    - future bug-fix overlap
    - future bug-fix within 50 commits
    """

    repository = Path(repository_path)

    commits = get_commit_history(
        repository,
        max_commits,
    )

    chronological_commits = list(
        reversed(commits)
    )

    commit_pairs = create_commit_pairs(
        commits
    )

    bug_fix_cache = build_bug_fix_cache(
        repository,
        chronological_commits,
    )

    dataset = []

    for index, (old_commit, new_commit) in enumerate(
        commit_pairs
    ):
        changed_files = get_changed_files(
            repository,
            old_commit,
            new_commit,
        )

        if not changed_files:
            continue

                # Commits after the current change,
        # restricted to the selected historical window.
        later_commits = chronological_commits[
            index + 2:
        ]

        # A 50-commit future label is only valid when
        # the complete 50-commit future window exists.
        if len(later_commits) < 50:
            continue
        change_metrics = get_change_metrics(
            repository,
            old_commit,
            new_commit,
        )

        # Build the dependency graph from the OLD commit
        # so the current change does not contaminate the graph.
        with temporary_checkout(
            repository,
            old_commit,
        ):
            graph = build_dependency_graph(
                repository
            )

            features = build_change_features(
                graph,
                changed_files,
                change_metrics,
            )

        commit_subject = get_commit_subject(
            repository,
            new_commit,
        )

        commit_label = classify_commit(
            commit_subject,
        )

        evidence_score = calculate_evidence_score(
            commit_subject,
            changed_files,
        )

        evidence_level = get_evidence_level(
            evidence_score,
        )

        for record in features:
            record["old_commit"] = old_commit
            record["new_commit"] = new_commit
            record["commit_subject"] = commit_subject
            record["commit_label"] = commit_label
            record["evidence_score"] = evidence_score
            record["evidence_level"] = evidence_level

            future_distance = get_future_bug_fix_distance(
                record["file"],
                later_commits,
                bug_fix_cache,
            )

            record["future_bug_fix_distance"] = (
                future_distance
            )

            record["future_bug_fix_overlap"] = int(
                future_distance > 0
            )

            record["future_bug_fix_50"] = int(
                0 < future_distance <= 50
            )

            dataset.append(record)

    return dataset