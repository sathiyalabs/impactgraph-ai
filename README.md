# ImpactGraph AI

> Dependency-aware machine learning for predicting future bug-fix risk in Git commits.

ImpactGraph AI analyzes a Git commit, combines code-change metrics with dependency-graph impact, and uses a machine-learning model to estimate whether changed code is likely to require a future bug fix.

The core idea is simple:

**A change can be risky not only because of how much code it modifies, but also because of how many parts of the codebase depend on it.**

---

## Overview

Traditional change-risk models often rely primarily on metrics such as:

- Lines added
- Lines deleted
- Total lines changed

ImpactGraph AI adds structural information from the repository's dependency graph:

- Direct dependency impacts
- Indirect dependency impacts

These signals are combined and passed to a Random Forest classifier.

```text
Git Commit
    │
    ├── Changed files
    └── Line-change metrics
             │
             ▼
    Dependency Graph
             │
             ├── Direct impacts
             └── Indirect impacts
             │
             ▼
      Feature Engineering
             │
             ▼
      Random Forest Model
             │
             ▼
      Risk Probability
             │
             ▼
        Flask API
             │
             ▼
       React Dashboard