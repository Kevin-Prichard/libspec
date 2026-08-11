# libspec

[![PyPI](https://img.shields.io/pypi/v/libspec.svg)](https://pypi.org/project/libspec/)
[![CI/CD](https://github.com/drhodes/libspec/actions/workflows/ci.yml/badge.svg)](https://github.com/drhodes/libspec/actions/workflows/ci.yml)
[![Documentation](https://github.com/drhodes/libspec/actions/workflows/docs.yml/badge.svg)](https://drhodes.github.io/libspec/)
[![License](https://img.shields.io/github/license/drhodes/libspec.svg)](https://github.com/drhodes/libspec/blob/main/LICENSE)

> **an ounce of spec is worth a pound of tokens**

`libspec` is a **Specification Management System** in Python. Features and
requirements are declared as Python classes; their docstrings are compiled into
content-addressed snapshots, diff'd over time, and served to LLM coding agents
via MCP.

### The deepest capability: generic specifications

The most powerful thing `libspec` enables is **generic specifications** —
published base classes that encode *how features should be documented and
specified*, not what any particular feature does.

```python
from libspec import Feature
from libspec.diataxis import Diataxis        # pip install libspec-diataxis
from libspec.conventioncommits import Commit # pip install libspec-conventioncommits

# Inherit once at your project base class.
class MyFeature(Feature, Diataxis, Commit): pass

# Every downstream feature automatically carries both contracts —
# enforced at spec-generation time, not as a style guide to forget.
class AwesomeNavBar(MyFeature):
    def tutorial(self):    return "In this tutorial we will build..."
    def how_to(self):      return "To highlight the active route..."
    def reference(self):   return "AwesomeNavBar(items, active_index, ...)"
    def explanation(self): return "The nav bar uses a slot-based model because..."
```

Miss a quadrant and `UnimplementedMethodError` tells you exactly where.
The contract propagates through inheritance automatically. See
[Generic Specifications](https://drhodes.github.io/libspec/explanation/generic-specs/)
for the full picture.

---


### Example Spec

Here is the specification `spec/err.py` used to establish fundamental code quality, error handling, and robustness constraints across the entire project via multiple inheritance:

```python
from libspec import Ctx, Feature, Requirement


# The Err docstrings are compiled into specification snapshots and 
# injected as prompt context for LLM code generation.
class Err(Ctx):
    """
    It is important that error handling be done excellently.

    If a function can fail, then it needs to do so in the most elegant way
    possible. Error reporting, handling, exceptions and all aspects of failure
    must be taken to extreme. It should be possible to understand the program
    by reading the error messages.

    When an error occurs there should be a story about the failure at each step
    of the way. What went wrong and why.
    """


class BoilerPlate(Ctx):
    """
    If you can see a way to reduce boiler plate, then do it.
    """


class FunctionLines(Ctx):
    """
    Try to keep functions under 20 lines.
    """


class Indentation(Ctx):
    """
    Try to keep indentation under 4 levels.
    """


class PreCondition(Ctx):
    """
    Functions should validate preconditions at their entry point.

    Instead of using `assert` statements (which can be disabled globally),
    raise explicit, descriptive exceptions (e.g., ValueError, TypeError, or
    custom domain exceptions) to robustly reject malformed input.
    """


class GlobalMutableState(Ctx):
    """
    Broadly you should avoid global mutable state.
    """


class PostCondition(Ctx):
    """
    Before a function returns, it should verify postconditions to ensure
    invariant properties hold true.

    Raise explicit, descriptive exceptions (such as RuntimeError or domain
    exceptions) rather than using `assert` statements to handle post-execution
    verification failures.
    """


# Composite specification aggregating precondition, postcondition, and global state avoidance guidelines.
class DefensiveProgramming(PreCondition, PostCondition, GlobalMutableState):
    pass


class Refactor(BoilerPlate, FunctionLines, Indentation):
    """
    Always keep an eye out for ways to generalize a function if it's utility
    might be helpful to other functions.

    Classes should be implemented in their own files with filename being the
    classname with correct naming convention
    """


class Robustness(DefensiveProgramming):
    """
    Always prioritize library-provided constructors for complex objects. Ensure
    all components are fully initialized before calling any state- mutating
    methods. Assume private internal state is uninitialized until the official
    constructor has returned. When extending library components, prioritize
    composition (pointers) over embedding by value to avoid risky state-copying
    bugs.

    Use dependency injection for system level objects for composability and to
    make testing easier.
    """


# Use multiple inheritance to endow Feature and Requirement specs with
# disciplined error handling guidance from above.
class Feat(Err, Refactor, Robustness, Feature):
    pass


class Req(Err, Refactor, Robustness, Requirement):
    pass
```

# Ecosystem: `libspec.*` Extension Libraries

`libspec` is designed to be extended by independent, separately-published
packages that contribute new modules to the `libspec.*` namespace.  A single
line in `libspec/__init__.py` makes this possible:

```python
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)
```

This causes Python to search **every** `libspec/` directory on `sys.path`
when resolving `libspec.*` imports, so any installed sibling library is
discovered automatically — no coordination with the `libspec` maintainers
required.

### Example: mixing extensions

```python
from libspec import Feature
from libspec.diataxis import Diataxis        # pip install libspec-diataxis
from libspec.conventioncommits import Commit # pip install libspec-conventioncommits

class MyBaseFeature(Feature, Diataxis, Commit): pass

class AwesomeNavBar(MyBaseFeature):
    ...
```

### Writing your own extension

A sibling library needs only a single source file — no hooks, no `.pth`
tricks:

```
libspec-myextension/
└── src/
    └── libspec/
        └── myextension.py   ← your module, no __init__.py needed
```

```toml
# pyproject.toml
[tool.hatch.build.targets.wheel]
packages = ["src/libspec"]
```

See the [full guide](https://drhodes.github.io/libspec/how-to/extend-namespace/)
and [explanation](https://drhodes.github.io/libspec/explanation/namespace-extensions/)
in the docs.

---

# The Object Model 

Each class declares a specification fragment that is optionally a
Jinja2 template string. More about that later...

## Inheritance

Inheritance means "does this and more." The inherited superclass
docstrings are normative, but compiled spec snapshots preserve them as
references instead of prepending their prose into the child docstring.
Renderers such as `libspec diff` can expand those refs when a review
needs the inherited context.

## Mixins 

Mixins help get around the diamond problem. (TODO: write more about this)

## Versioning

Note that the versioning of `libspec` is still being hammered
out. Currently, the version of `libspec` appears in generated spec snapshots
(`libspec-version` field). But, how diffs will be performed on
different versions is unexplored.

## Feature Branch & Multi-Commit Spec Diffing

When working on feature branches with intermediate commits, running `uv run libspec diff` right after a commit will report `No changes detected` because `HEAD` matches the live spec on disk.

To track the cumulative specification delta across all intermediate commits on a feature branch, pass the base branch target:

```bash
uv run libspec diff main
```

This tracks all specification additions, requirement modifications, and docstring changes relative to `main` throughout multi-stage development workflows.
