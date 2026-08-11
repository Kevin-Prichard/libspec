# How to Install and Set Up Libspec

`libspec` is a Python library and CLI tool for spec-driven development with LLM agents.

---

## Prerequisites

- **Python**: Version 3.12 or higher.
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (recommended) or standard `pip`.

---

## Installation

### Using `uv` (Recommended)

Add `libspec` to your project dependencies:

```bash
uv add libspec
```

Or install it globally for CLI access:

```bash
uv tool install libspec
```

### Using `pip`

Install `libspec` directly from PyPI:

```bash
pip install libspec
```

---

## Initializing a Libspec Project

Inside your project root directory, run the initialization command:

```bash
uv run libspec init
```

This creates a `.libspec/` configuration directory and a default `spec/` folder containing an initial specification file.

---

## Next Steps

- Follow the [Quickstart Tutorial](../tutorials/quickstart.md) to author your first specification class.
- Learn how to connect your coding agent in [Using the MCP Server](agents.md).
