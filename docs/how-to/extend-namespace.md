# How to Build a `libspec.*` Extension Library

This guide shows you how to create and publish an independent Python package
that contributes a new module to the `libspec.*` namespace — for example
`libspec.diataxis`, `libspec.conventioncommits`, or any other domain-specific
extension.

**Prerequisite**: `libspec>=10.5.2` installed in your project.

---

## 1. Create the project

```bash
mkdir libspec-myextension
cd libspec-myextension
uv init --no-readme
```

---

## 2. Write your module

Create `src/libspec/myextension.py`. This is the **only** source file you need —
no `__init__.py`, no subdirectory:

```python
# src/libspec/myextension.py

from libspec import Feature, UnimplementedMethodError


class MyBase(Feature):
    """
    Feature Specification: {{feature_name}}

    {{description}}

    # My Section
    {{my_field}}
    """

    def my_field(self):
        raise UnimplementedMethodError()
```

---

## 3. Configure `pyproject.toml`

```toml
[project]
name = "libspec-myextension"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "libspec>=10.5.2",   # minimum version that includes extend_path
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/libspec"]   # ship the src/libspec/ directory into the wheel
```

!!! important
    `packages = ["src/libspec"]` is what places `myextension.py` inside the
    installed `libspec/` directory (or alongside it on `sys.path` for editable
    installs). Without this, the module will not be discoverable.

---

## 4. Install and verify

```bash
uv add libspec-myextension   # or: uv pip install -e .
```

Then in any project that depends on both `libspec` and `libspec-myextension`:

```python
from libspec.myextension import MyBase

class MyFeature(MyBase):
    def date(self):        return "2026-08-11"
    def description(self): return "My feature description."
    def my_field(self):    return "My field content."
```

---

## 5. Compose with other extensions

Because every sibling library contributes to the same `libspec.*` namespace,
users can mix and match freely via multiple inheritance:

```python
from libspec import Feature
from libspec.diataxis import Diataxis
from libspec.myextension import MyBase

class ProjectBase(Feature, Diataxis, MyBase): pass

class AwesomeWidget(ProjectBase):
    def date(self):        return "2026-08-11"
    def description(self): return "An awesome widget."
    def tutorial(self):    return "In this tutorial we will..."
    def how_to(self):      return "To configure, set..."
    def reference(self):   return "AwesomeWidget(x: int, ...)"
    def explanation(self): return "The widget uses a slot model because..."
    def my_field(self):    return "My extension field content."
```

---

## How it works

`libspec.__init__.py` contains:

```python
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)
```

This causes Python to search **all** `libspec/` directories on `sys.path` when
resolving `libspec.*` imports, not just the one inside `libspec`'s own
installation. Your `src/libspec/` directory is added to `sys.path` by the
editable install mechanism (or included directly in the wheel), so
`libspec.myextension` is discovered automatically.

See [The `libspec.*` Namespace Extension Model](../explanation/namespace-extensions.md)
for a deeper explanation of why this works.
