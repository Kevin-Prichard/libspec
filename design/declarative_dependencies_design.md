# Design: Spec-Native Declarative Component Dependencies (`depends_on`)

**Version:** 1.0.0
**Status:** Draft / Proposal
**Author:** Buffy (Freebuff agent) & Derek
**Date:** 2026-08-02
**Supersedes (declaration mechanism only):** [`dependencies_design_proposal.md`](dependencies_design_proposal.md)

---

## 1. Executive Summary

`libspec dependencies` currently reports **constraint inheritance** (`Component.inherits`) —
the MRO chain of cross-cutting *qualities* (`spec.err.Err`, `BoilerPlate`, `Robustness`, ...) that
we instill into the coding agent. Those are **not implementation dependencies**. A component like
`ScannerPersistenceReq` does not "depend on" `Err` to be built; it must merely be built *well*.

What an agent actually needs to sequence work is the **logical component-to-component dependency
graph**: which component's output/interface another consumes. Today that graph lives only in the
human's head (or an analyst's reading of the spec). This proposal makes it **declarative, spec-native,
and git-versioned**:

```python
class ScannerPersistenceReq(Req):
    """State persistence and scan resumption engine. ..."""
    depends_on = (TargetSelectionReq, ProbeClassificationReq, OutputSchemaReq)
```

and fixes `libspec dependencies` (CLI, MCP, REPL) to read **that** graph — plus adds a topological
sort (`--topo`) so agents get an implementation order sequenced for parallel work.

---

## 2. Motivation & Problem Statement

### 2.1 What `libspec dependencies` prints today is the wrong graph

The three consumers — `cli.py:dependencies`, `mcp_server.py:list_dependencies`,
`repl.py:DependenciesCommand` — all do:

```python
deps[comp.ref] = comp.inherits   # MRO constraint chain, NOT logical dependencies
```

For the EvilBitMap project this prints, for every component, the same ten constraint refs
(`libspec.spec_types.Feature`, `spec.err.BoilerPlate`, `spec.err.Err`, ...). It tells an agent
nothing about build order: **all 14 components are siblings** in that view.

### 2.2 The real graph is logical, and it exists today only by analysis

Reading the spec source (`spec/audit.py`, `spec/viz.py`) we derive a real DAG:

| Component | Depends on (logical) | Edge kind |
|---|---|---|
| `TargetSelectionReq` | — | root |
| `ProbeClassificationReq` | — | root |
| `GitHubPagesDeployFeat` | — | root (independent) |
| `OutputSchemaReq` | `ProbeClassificationReq` | data contract (verdict enums) |
| `ScannerPersistenceReq` | `TargetSelectionReq`, `ProbeClassificationReq`, `OutputSchemaReq` | orchestration + contract |
| `DataIngestionReq` | `OutputSchemaReq` | data contract (JSON schema) |
| `HilbertCanvas800Req` | `DataIngestionReq` | composition (spatial index) |
| `IPInfoPanelReq` | `DataIngestionReq` | composition (probe metadata) |
| `EvilBitAuditApp` | all four audit components | orchestration |
| `ReticleZoomViewportReq` | `HilbertCanvas800Req` | rendering layering |
| `PortFilterReq` | `HilbertCanvas800Req`, `DataIngestionReq` | composition |
| `KPIAndExplorerFeat` | `PortFilterReq`, `DataIngestionReq` | composition |
| `AuditCliFeat` | `EvilBitAuditApp` | orchestration |
| `StaticWebApp` | every viz component | composition (app shell) |

This is exactly the information a planner needs. It should be **in the spec**, not in a doc.

### 2.3 Prior proposal was the wrong mechanism for declaration

`dependencies_design_proposal.md` (2026-06-08) proposed an **agent-driven transactional append-only
log**: the agent calls `store_dependency(ref, depends_on, snapshot_id="PENDING")` during the session,
with binding to the real snapshot at `git commit`. That mechanism:

- **Puts the source of truth outside the spec** (in `.libspec/libspec.jsonl`), so it is invisible in
  spec diffs and reviewable only via log spelunking.
- **Depends on agent discipline** (the agent must remember to record each edge).
- **Requires halting/rollback machinery** for aborted sessions.

The spec-native declaration below is simpler: edges are plain class attributes, versioned with the
spec, visible in `libspec diff`, and impossible to forget once written. The append-only log remains
useful for **implementation claims** (`implemented` records), which this proposal does not touch.

---

## 3. Design Tenets

1. **Source of truth = the spec classes.** Edges live in `spec/*.py`, are diffed by `libspec diff`,
   and are reviewed in the same PR as the code.
2. **Declarative, zero-boilerplate.** One attribute, one line per edge. No registry, no decorators.
3. **Two orthogonal axes.** `inherits` = constraint qualities instilled into the agent (ambient,
   inherited). `depends_on` = logical implementation ordering (explicit, per-component, not inherited).
4. **The graph must be a DAG.** Cycles are a compile-time error with the cycle path printed.
5. **Deterministic resolution.** Class objects resolve to FQNs at compile time; the graph is a
   stable, sortable set of string refs.

---

## 4. The Python Syntax

Declare edges as a class attribute on the component:

```python
# spec/audit.py
class OutputSchemaReq(Req):
    """JSON output schema specification for evilbit_audit.json: ..."""
    depends_on = (ProbeClassificationReq,)          # verdict enums are part of the schema

class ScannerPersistenceReq(Req):
    """State persistence and scan resumption engine. ..."""
    depends_on = (TargetSelectionReq, ProbeClassificationReq, OutputSchemaReq)

class EvilBitAuditApp(Req):
    """..."""
    depends_on = (TargetSelectionReq, ProbeClassificationReq,
                  ScannerPersistenceReq, OutputSchemaReq)

class AuditCliFeat(Feat):
    """..."""
    depends_on = (EvilBitAuditApp,)
```

```python
# spec/viz.py
class DataIngestionReq(Req):
    """JSON and JSONB dataset parser. ..."""
    depends_on = (OutputSchemaReq,)                 # cross-domain contract edge

class HilbertCanvas800Req(Req):
    """Fixed 800x800 HTML Canvas Hilbert terrain map renderer. ..."""
    depends_on = (DataIngestionReq,)

class ReticleZoomViewportReq(Req):
    """Dual-view reticle magnifying system. ..."""
    depends_on = (HilbertCanvas800Req,)

class KPIAndExplorerFeat(Feat):
    """Dashboard features ..."""
    depends_on = (PortFilterReq, DataIngestionReq)

class StaticWebApp(Req):
    """Zero-dependency static Web application ..."""
    depends_on = (DataIngestionReq, HilbertCanvas800Req, ReticleZoomViewportReq,
                  IPInfoPanelReq, PortFilterReq, KPIAndExplorerFeat)
```

### 4.1 Rules

- **Type:** a `tuple` (or `list`) of spec component **classes**, or **FQN strings** for forward
  references and external specs. Tuples are preferred (immutability); order is insignificant.
- **Not inherited:** `depends_on` is read off each concrete class only. Constraint specs
  (`Err`, `Refactor`, ...) and the `Feat`/`Req` mixins never declare it. Rationale: qualities are
  ambient and inherited; *dependencies are explicit per-component* — silently merging base-class
  edges into every subclass would couple siblings we never intended to couple.
- **Not recorded on constraint classes:** dependency-stub components (`is_dependency=True`, e.g. the
  `spec.err.*` stubs emitted by the compiler) always carry `depends_on=[]`.

### 4.2 Alternatives considered

| Option | Verdict |
|---|---|
| Class attribute `depends_on = (...)` | **Adopted** — plain, reviewable, testable. |
| Metaclass / `__init_subclass__` kwargs (`class X(Req, depends_on=...)`) | Rejected — not valid Python; args on the class line are constructor args. |
| Decorator (`@depends_on(A, B)`) | Rejected — splits declaration from class, harder to grep, extra import. |
| String FQNs everywhere | Rejected as primary — classes give IDE refactoring and cycle-check safety; strings allowed as escape hatch. |

---

## 5. Semantics of an Edge

`Y.depends_on = (X,)` means: **"X's interface/output must exist before Y can be built or tested."**
Three edge kinds cover the cases observed in real specs:

1. **Data contract** — one component's output schema is another's input:
   `OutputSchemaReq → DataIngestionReq` (the `evilbit_audit.json` schema is the contract).
2. **Orchestration** — a component wires other modules together:
   `EvilBitAuditApp → {TargetSelectionReq, ProbeClassificationReq, ScannerPersistenceReq, OutputSchemaReq}`.
3. **Composition / layering** — a component builds on another's renderer/index:
   `ReticleZoomViewportReq → HilbertCanvas800Req`.

The compiler does not need to distinguish kinds; the consumer (planner/agent) does. The docstring of
each component documents the *nature* of the edge; `depends_on` records its *existence*.

---

## 6. Data Model Change (`libspec/common.py`)

Add a defaulted field so old serialized snapshots remain readable:

```python
@dataclass(frozen=True)
class Component:
    ref: str
    docstring: str
    is_template: bool
    inherits: list[str]
    hash: str
    is_dependency: bool = False
    depends_on: list[str] = field(default_factory=list)   # NEW: logical edges, FQN strings
```

- `__post_init__` validation extended: `depends_on` must be a list of non-empty strings
  (mirroring `inherits` validation).
- JSON serialization in the store includes `depends_on` when present; absence in historical records
  decodes to `[]`.

---

## 7. Compile-Time Resolution & Validation (`libspec/spec.py`)

In `Spec.get_components()`, at both `Component(...)` construction sites (full specs and dependency
stubs):

1. For each **full** spec class, read `getattr(spec_cls, "depends_on", ())`.
2. Resolve each element:
   - a class → `fqn(element)` (already available in `libspec.spec`);
   - a string → validate it matches a known compiled component ref.
3. Validate (fail loudly, per `spec.err.PreCondition` / `spec.err.Err` — explicit, descriptive
   exceptions, never `assert`):
   - **Unknown ref** → `SpecCompileError(f"{ref} declares depends_on {unknown}, which is not a known spec component")`.
   - **Self-dependency** → `SpecCompileError("... depends on itself")`.
   - **Cycle** → run the same Kahn/DFS used by `--topo`; on failure raise
     `SpecCycleError` with the full cycle path, e.g.
     `A -> B -> C -> A`.
4. Deduplicate and sort the resolved FQN list for deterministic hashing.
5. Dependency stubs (`is_dependency=True`) get `depends_on=[]`.

The **master hash** (`write_xml`) and snapshot ID automatically change when edges change, so `libspec
diff` detects dependency drift as part of the component record hash.

---

## 8. Consumer Fixes — the `dependencies` command

All three consumers switch from `inherits` to `depends_on` (identical fix):

| Consumer | Location | Change |
|---|---|---|
| `cli.py` | `dependencies` command | `deps[comp.ref] = comp.inherits` → `comp.depends_on` |
| `mcp_server.py` | `list_dependencies` tool | `deps[comp.ref] = list(comp.inherits)` → `list(comp.depends_on)` |
| `repl.py` | `DependenciesCommand` | `deps[comp.ref] = comp.inherits` → `comp.depends_on` |

### 8.1 New default output

```
Component Dependencies for 'HEAD (Live Spec)':
  • spec.audit.ScannerPersistenceReq
    └── depends on: spec.audit.ProbeClassificationReq
    └── depends on: spec.audit.OutputSchemaReq
    └── depends on: spec.audit.TargetSelectionReq
  • spec.viz.DataIngestionReq
    └── depends on: spec.audit.OutputSchemaReq
```

### 8.2 Optional flags (backward-compatible view)

- `--inherits` — additionally print constraint inheritance, explicitly labeled
  `inherits (constraint): ...` so the two axes are never confused.
- `--topo` — print the topological order (Section 9) instead of the adjacency view.

`spec_diff.py` additionally reports `depends_on: [..] -> [..]` in `[CHANGED]` entries alongside the
existing `inherits` change detection (same `_diff_components` pattern).

---

## 9. New Capability — Implementation Ordering (`--topo` / `libspec topo`)

Add a small Kahn's-algorithm topological sort over `depends_on` edges:

- `libspec/util.py`: `topological_sort(components) -> list[list[str]]` returning **wave groups** —
  nodes whose longest dependency path has equal depth are grouped, so each wave can be handed to
  parallel agents with no cross-wave interference.
- CLI: `uv run libspec dependencies --topo` and/or `uv run libspec topo`.
- MCP: `implementation_order(commit=None)` tool; REPL: `topo` command.

### 9.1 Example output (EvilBitMap, derived from Section 2.2)

```
Topological order for 'HEAD (Live Spec)':            # contract first, then two lanes
  Wave 1: spec.audit.TargetSelectionReq,
          spec.audit.ProbeClassificationReq,
          spec.viz.GitHubPagesDeployFeat            (3 parallel agents)
  Wave 2: spec.audit.OutputSchemaReq                (the cross-domain contract)
  Wave 3: spec.audit.ScannerPersistenceReq,
          spec.viz.DataIngestionReq                 (2 parallel agents)
  Wave 4: spec.audit.EvilBitAuditApp,
          spec.viz.HilbertCanvas800Req,
          spec.viz.IPInfoPanelReq                   (3 parallel agents)
  Wave 5: spec.audit.AuditCliFeat,
          spec.viz.ReticleZoomViewportReq,
          spec.viz.PortFilterReq                    (3 parallel agents)
  Wave 6: spec.viz.KPIAndExplorerFeat
  Wave 7: spec.viz.StaticWebApp
```

Rules:
- Roots (in-degree 0) emit first; a node emits when all its `depends_on` are emitted.
- Cycles make the sort impossible → the same `SpecCycleError` as compilation, with the path.
- Ties within a wave are ordered by FQN for determinism.

---

## 10. Relationship to `dependencies_design_proposal.md`

| Concern | June 8 proposal | This proposal |
|---|---|---|
| Where edges are declared | Agent writes `dependency` events to `libspec.jsonl` (`store_dependency`, `PENDING` snapshot) | Author writes `depends_on` class attributes in `spec/*.py` |
| Visibility in spec review | Log records only | First-class in `libspec diff` / component records |
| Snapshot binding | Replay binds `PENDING` at commit | Declarations are part of the compiled snapshot from birth |
| Agent discipline | Required per-session | None — edges are compiled, never forgotten |
| Halt/rollback | Git-native discard of log entries | N/A — declarations revert with the spec edit |
| Retained | `implemented` claims, append-only store, `vcs_link` | unchanged |
| `declare_dependency` MCP tool | proposed | **dropped** — unnecessary; source is authoritative |

---

## 11. Testing Plan

1. **`common.py`** — `Component` rejects non-string/non-list `depends_on`.
2. **`spec.py` resolution** — class refs → FQNs; string refs validated; unknown ref raises
   `SpecCompileError`; self-dep raises; duplicate edges deduplicated.
3. **Cycle detection** — diamond graph passes; `A→B→C→A` raises `SpecCycleError` with path.
4. **`dependencies` consumers** — CLI/MCP/REPL output contains only declared edges; `--inherits`
   labels constraints; `--topo` groups a diamond (`A; B,C; D`) into the expected waves.
5. **`spec_diff`** — changing `depends_on` on a component yields a `[CHANGED]` entry reporting the
   edge delta and a new master hash.
6. **Regression** — regenerate `tests/spec-build/` XML fixtures; existing snapshots without
   `depends_on` still decode (default `[]`).

---

## 12. Rollout & Dogfooding

1. Land the core change in `libspec` (data model, compiler, three consumers, `--topo`, tests).
2. Annotate the **EvilBitMap** spec (`spec/audit.py`, `spec/viz.py`) with the `depends_on`
   declarations from Section 4 — the first real adoption, exercised by `uv run libspec
   dependencies --topo` and the `post-implement` workflow gates.
3. Propagate to other libspec projects as they touch their specs; the old behavior stays available
   via `--inherits` during transition.
