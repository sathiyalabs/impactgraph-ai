import sys

from analyzer.history import build_history_dataset
from analyzer.dataset import save_features_to_csv


def generate_dataset(
    repository_path: str,
    output_path: str,
    max_commits: int = 50,
) -> int:
    """
    Generate a historical feature dataset for a repository.
    """

    print("ImpactGraph AI")
    print("=" * 50)

    print(f"Repository: {repository_path}")
    print(f"Commits: {max_commits}")
    print()

    data = build_history_dataset(
        repository_path,
        max_commits,
    )

    if not data:
        raise ValueError(
            "No training examples have a complete 50-commit future window. "
            "Use a repository with at least 52 commits and Python changes. "
            "The output file has not been changed."
        )

    save_features_to_csv(
        data,
        output_path,
    )

    print(f"Records generated: {len(data)}")
    print(f"Dataset: {output_path}")

    return len(data)


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python -m analyzer.generate_dataset "
            "<repository> <output.csv> [max_commits]"
        )
        return

    repository_path = sys.argv[1]
    output_path = sys.argv[2]

    max_commits = (
        int(sys.argv[3])
        if len(sys.argv) >= 4
        else 50
    )

    generate_dataset(
        repository_path,
        output_path,
        max_commits,
    )


if __name__ == "__main__":
    main()
