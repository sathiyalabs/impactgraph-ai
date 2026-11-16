# ImpactGraph AI

> Dependency-aware machine learning for predicting future bug-fix risk in Git commits.

ImpactGraph AI analyzes Git commits and combines code-change metrics with dependency-graph impact to estimate future bug-fix risk at the file and commit level.

The core idea is:

**A change can be risky not only because of how much code it modifies, but also because of how many parts of the codebase depend on the changed code.**

---

## Overview

Traditional change-risk models often rely primarily on:

- Lines added
- Lines deleted
- Total lines changed

ImpactGraph AI adds structural information from the repository dependency graph:

- Direct dependency impacts
- Indirect dependency impacts

These signals are combined with change metrics and passed to a Random Forest classifier.

```text
Git Commit
    |
    +-- Changed files
    +-- Change metrics
            |
            v
    Dependency Graph
            |
            +-- Direct impacts
            +-- Indirect impacts
            |
            v
    Feature Engineering
            |
            v
    Random Forest Model
            |
            v
    Risk Probability
            |
            v
        Flask API
            |
            v
      React Dashboard
```

## Local setup and verification

Use Python 3.12 and install `requirements.txt` in a virtual environment. The integration tests use a pinned, read-only Flask checkout, which is intentionally excluded from this repository:

```sh
python -m pip install -r requirements.txt
python scripts/setup_test_repository.py
python -m pytest -q
```

The fixture setup downloads only the pinned commit and its parent. It refuses to overwrite an existing checkout. The new history/checkout regression tests create their own temporary repositories.

Dataset generation fetches the requested historical window plus 50 commits of future-label evidence. A repository needs at least 52 commits with relevant Python changes for the first labeled example. Insufficient history raises an actionable error without overwriting an existing dataset. Temporary analysis restores the original branch or detached HEAD.
