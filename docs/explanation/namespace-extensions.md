# The `libspec.*` Namespace Extension Model

`libspec` is designed to be extended. Third-party libraries can contribute
new modules under the `libspec.*` namespace — so users can write:

```python
from libspec import Feature
from libspec.diataxis import Diataxis
from libspec.conventioncommits import Commit

class MyBaseFeature(Feature, Diataxis, Commit): pass
```

Each of those imports comes from a **different, independently-published package**,
but they all feel like part of one coherent library. This page explains how that
works and why it was designed this way.

---

## The problem: regular packages are closed

When Python imports `libspec`, it records one location for the package:

```
libspec.__path__ = ['.../site-packages/libspec']
```

Any subsequent `from libspec.X import Y` looks **only** in that one directory.
A separate installed package that ships a `libspec/X.py` file will simply never
be found, even if it is on `sys.path`.

This is fine for single-publisher packages, but it makes ecosystem composability
impossible — you would have to fork `libspec` or vendor everything into a
monorepo to achieve the same import experience.

---

## The solution: `pkgutil.extend_path`

`libspec` opts into namespace extension with a single line at the top of its
`__init__.py`:

```python
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)
```

`pkgutil.extend_path` walks **every entry on `sys.path`**, looks for a
sub-directory (or `.pth` file) named `libspec`, and appends any it finds to
`libspec.__path__`. The result is that `libspec.__path__` becomes a list of
every `libspec/` directory across all installed packages:

```
libspec.__path__ = [
    '.../site-packages/libspec',       # libspec itself
    '.../libspec-diataxis/src/libspec', # libspec-diataxis (editable)
    '.../site-packages/libspec',        # libspec-conventioncommits, etc.
]
```

Python's import machinery then searches all of them in order, so
`libspec.diataxis` and `libspec.conventioncommits` are discovered naturally.

---

## What a sibling library looks like

A sibling library needs nothing beyond a single source file and a standard
`pyproject.toml`. No hooks, no `.pth` tricks, no modifications to `libspec`:

```
libspec-diataxis/
└── src/
    └── libspec/
        └── diataxis.py     ← just a file; no __init__.py needed
```

```toml
# pyproject.toml
[project]
name = "libspec-diataxis"
dependencies = ["libspec>=10.5.2"]

[tool.hatch.build.targets.wheel]
packages = ["src/libspec"]
```

When installed (including in editable mode via `uv add`), the package's
`src/` directory lands on `sys.path`. `pkgutil.extend_path` then finds
`src/libspec/` and adds it to `libspec.__path__` automatically.

---

## Why a module file, not a package directory?

`libspec.diataxis` is a plain `.py` file, not a `diataxis/` directory with an
`__init__.py`. This is intentional:

- A module file needs no `__init__.py` — it *is* the module.
- A namespace package directory (`diataxis/` without `__init__.py`) would be
  an empty container with no attributes — `from libspec.diataxis import Diataxis`
  would fail.
- A regular package directory (`diataxis/` *with* `__init__.py`) works, but
  adds a layer of indirection for no benefit when the entire public surface is
  a single class.

The simplest shape that makes `from libspec.diataxis import Diataxis` work is
a file called `diataxis.py`. That is what sibling libraries should ship.

---

## The contract for sibling library authors

To publish a `libspec.*` sibling library:

1. Declare `libspec>=10.5.2` as a dependency (the minimum version that includes
   `extend_path`).
2. Ship your module at `src/libspec/<name>.py`.
3. Set `packages = ["src/libspec"]` in `pyproject.toml`.
4. Done — no hooks, no coordination with the `libspec` maintainers required.

See [How to build a `libspec.*` extension library](../how-to/extend-namespace.md)
for a step-by-step guide.
