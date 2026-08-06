# Feature Branch & Multi-Commit Specification Diffing

When developing on a feature branch with incremental commits (e.g., implementing in stages from Tier 1 through Tier 4), running a default `uv run libspec diff` after committing will output `No changes detected` because `HEAD` matches the live specification files on disk.

To track the **cumulative specification footprint and evolution across intermediate commits** on a feature branch, diff back to the base branch or starting commit reference (such as `main` or `master`).

---

## 1. Diffing Against Base Branch (`main`)

To view all specification changes, additions, and docstring modifications introduced across your feature branch relative to `main`:

```bash
# Diff live specification against base branch (main)
uv run libspec diff main

# Diff live specification against a specific commit hash
uv run libspec diff d777f29
```

This technique ensures that:
* Newly added requirement classes and features are tracked across multi-commit development cycles.
* Uncommitted and committed spec changes are compared holistically against the base branch before merging.

---

## 2. Incorporating into Developer Agent Workflows

When guiding an LLM coding agent (via MCP or CLI), instruct the agent to run:

```bash
uv run libspec diff main
```

This provides the agent with the complete specification delta for the entire feature branch rather than just uncommitted changes in the latest working tree step.
