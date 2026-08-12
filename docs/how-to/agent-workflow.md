# How to Execute the Developer Agent Workflow

The `agent-workflow` command outputs the standardized 8-step development loop for coding agents and developers working with `libspec`.

---

## Running the Command

Generate workflow instructions formatted for your active environment:

```bash
uv run libspec agent-workflow
```

Optionally specify your agent platform (`antigravity`, `gemini`, or `claude`):

```bash
uv run libspec agent-workflow --agent antigravity
```

---

## The 9-Step Developer Agent Loop

1. **Edit Spec**: Decompose broad requirements into granular, single-responsibility specification classes in `spec/`.
2. **Diff Spec (MANDATORY BEFORE CODING)**: Run `uv run libspec diff` (or `mcp_libspec_diff`) to inspect specification drift and review mutations.
3. **Sort Implementation Ordering**: Inspect component dependencies via `uv run libspec dependencies` to sort components into topological order.
4. **Test-Driven Development**: Write unit tests for components in topological dependency order.
5. **Implement**: Implement code to satisfy the tests.
   - Run tests: `make test`
   - Check formatting: `uv run ruff format --check`
   - Run linter: `uv run ruff check`
6. **Code Quality & Verification**: Run static analysis, type checking (`mypy`), and dead code detection (`vulture`).
7. **Verify Specification Sync**: Run `uv run libspec diff` to ensure live specs are synchronized with the final implementation.
8. **Version Bump**: Bump the project version in `pyproject.toml` according to Semantic Versioning (`MAJOR.MINOR.PATCH`) using helper target commands (`make bump-patch`, `make bump-minor`, or `make bump-major`).
9. **Commit & Present**: Author a concise git commit message and present the changes.
