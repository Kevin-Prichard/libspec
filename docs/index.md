# libspec

> **"An ounce of spec is worth a pound of tokens."**

`libspec` is a **Specification Management System** in Python. Similar in spirit to Object-Relational Mapping (ORM) tools, `libspec` implements **Object Specification Mapping (OSM)** to compile logical requirements declared in Python classes into structured database snapshots. Instead of generating SQL schemas, it tracks how requirement definitions evolve over time.

By diff'ing snapshots and providing a native **Model Context Protocol (MCP)** server, `libspec` acts as a centralized, programmatic context layer for LLM coding agents. The developer workflow is incremental and exploratory, turning code generation from a gamble into disciplined delegation.

---

## The big idea: generic specifications

The deepest capability in `libspec` is **generic specifications** — base classes
that encode *how features should be specified*, not what any particular feature
does.

```python
from libspec import Feature
from libspec.diataxis import Diataxis        # pip install libspec-diataxis
from libspec.conventioncommits import Commit # pip install libspec-conventioncommits

# Inherit once. Every feature in your project automatically
# carries both contracts — enforced at spec-generation time.
class MyFeature(Feature, Diataxis, Commit): pass

class AwesomeNavBar(MyFeature):
    def tutorial(self):    return "In this tutorial we will build..."
    def how_to(self):      return "To highlight the active route..."
    def reference(self):   return "AwesomeNavBar(items, active_index, ...)"
    def explanation(self): return "The nav bar uses a slot-based model because..."
```

Generic specs turn documentation standards from advisory suggestions into
**structural guarantees**. Miss a quadrant and `UnimplementedMethodError` tells
you exactly where, at spec-generation time. The contract travels through
inheritance automatically — define it once at your base class, and every
downstream feature complies.

[Read the full explanation →](explanation/generic-specs.md)

---

## The Workflow

```mermaid
graph TD
    A[Define Spec in Python] --> B[Compile & Track in SpecStore]
    B --> C[Inspect via REPL or Diff]
    C --> D[Connect LLM Agent via MCP]
    D --> E[Agent Reads Spec & Implements Code]
    E --> F[Test & Repeat]
    style A fill:#1A237E,stroke:#3F51B5,stroke-width:2px,color:#fff
    style B fill:#006064,stroke:#00838F,stroke-width:2px,color:#fff
    style F fill:#2E7D32,stroke:#4CAF50,stroke-width:2px,color:#fff
```

---

## Core Philosophy

1. **Specifications as Code**: Define requirements as declarative Python classes. Use inheritance to express dependencies and mixins to compose guidelines.
2. **Version-Controlled Design**: Save specification snapshots directly into `SpecStore` (a lightweight, append-only SQLite transaction ledger).
3. **Seamless Agent Guidance**: Feed rich, dependency-sorted context directly to coding agents via LSP or MCP, ensuring they implement requirements correctly.
4. **Zero Boilerplate**: Offload relationship tracking to the transaction log instead of polluting specification files with manual wiring.

---

## Visualizing the Architecture

`libspec` bridges the gap between design-time specifications and run-time implementations. It provides tools for both human developers and LLM subagents:

*   **Developers** write and refine specifications using familiar Python OOP syntax.
*   **The Compiler** builds these specs into content-addressed XML/JSON snapshots.
*   **The REPL & CLI** allow you to inspect, search, and diff specification snapshots.
*   **The MCP Server** exposes these tools directly to coding assistants.
