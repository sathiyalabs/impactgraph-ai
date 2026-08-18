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