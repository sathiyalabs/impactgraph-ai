import sys
from pathlib import Path

from analyzer.git import get_changed_files
from analyzer.graph import build_dependency_graph
from analyzer.impact import find_impacted_files
from analyzer.scoring import calculate_impact_score, get_risk_level


def main() -> None:
    if len(sys.argv) != 4:
        print(
            "Usage: python -m analyzer.main "
            "<repository_path> <old_commit> <new_commit>"
        )
        return

    repository_path = Path(sys.argv[1])
    old_commit = sys.argv[2]
    new_commit = sys.argv[3]

    try:
        print("\nImpactGraph AI")
        print("=" * 50)

        # 1. Build dependency graph
        graph = build_dependency_graph(repository_path)

        print(f"Files analyzed: {graph.number_of_nodes()}")
        print(f"Dependencies found: {graph.number_of_edges()}")

        # 2. Detect changed files
        changed_files = get_changed_files(
            str(repository_path),
            old_commit,
            new_commit,
        )

        print("\nChanged Files")
        print("-" * 50)

        for file in changed_files:
            print(f"  -> {file}")

        # 3. Normalize graph paths
        normalized_graph_files = {
            node.replace("\\", "/"): node
            for node in graph.nodes
        }

        all_impacted_files = set()

        print("\nImpact Analysis")
        print("-" * 50)

        for changed_file in changed_files:
            normalized_changed_file = changed_file.replace("\\", "/")

            print(f"\nChanged: {normalized_changed_file}")

            graph_file = normalized_graph_files.get(
                normalized_changed_file
            )

            if graph_file is None:
                print("  No dependency information available.")
                continue

            # Find impacted files
            impacted = find_impacted_files(
                graph,
                graph_file,
            )

            if impacted:
                print("Potentially impacted:")

                for file in sorted(impacted):
                    print(f"  -> {file}")

                all_impacted_files.update(impacted)

            else:
                print("  No dependent files found.")

            # Direct dependencies
            direct_impacts = len(
                list(graph.predecessors(graph_file))
            )

            # Indirect dependencies
            indirect_impacts = len(impacted) - direct_impacts

            # Calculate score
            score = calculate_impact_score(
                direct_impacts,
                indirect_impacts,
            )

            risk = get_risk_level(score)

            print(f"\nImpact Score: {score}/100")
            print(f"Risk Level: {risk}")

        # 4. Summary
        print("\nSummary")
        print("-" * 50)
        print(f"Changed files: {len(changed_files)}")
        print(
            f"Potentially impacted files: "
            f"{len(all_impacted_files)}"
        )

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()