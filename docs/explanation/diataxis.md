# Diátaxis Documentation Principles in Libspec

`libspec` documentation is structured according to **Diátaxis**, a systematic framework for technical documentation authoring.

---

## The Four Quadrants

Diátaxis organizes content based on user needs across two fundamental axes:

| | **Acquisition (Study)** | **Application (Work)** |
|---|---|---|
| **Action (Doing)** | **Tutorials** (Learning-oriented) | **How-To Guides** (Goal-oriented) |
| **Cognition (Knowing)** | **Explanation** (Understanding-oriented) | **Reference** (Information-oriented) |

---

## How Libspec Applies Diátaxis

1. **Tutorials (`docs/tutorials/`)**: Take the developer by the hand through building their first spec-driven project. Focus strictly on learning by doing.
2. **How-To Guides (`docs/how-to/`)**: Provide goal-oriented directions for specific developer tasks (installing, running agent workflows, diffing feature branches, configuring MCP).
3. **Reference (`docs/reference/`)**: Technical descriptions of the CLI subcommands, MCP tool contracts, and Python API classes. Purely factual, accurate, and complete.
4. **Explanation (`docs/explanation/`)**: Conceptual deep-dives into Object Specification Mapping (OSM), store architecture, content hashing, and transaction logs.
