# Generic Specifications: Reusable Contracts for Features

The most powerful idea in `libspec` is not that you can write specifications —
it is that you can write specifications *about how to write specifications*, and
then inherit them.

This page explores what that means, why it matters, and what becomes possible
when you think of specification structure as something that can be published,
versioned, and composed like any other library dependency.

---

## The problem specifications solve — and the problem they create

Every non-trivial software project eventually produces documentation that is
incomplete, inconsistent, and structured differently in every corner. Some
features have tutorials. Others have only API references. A few have detailed
explanations buried in commit messages. The information exists, but it is
scattered and untrustworthy.

The usual remedy is a documentation standard: a style guide, a template, a
wiki page titled *"How We Document Features Here."* This works — until it
doesn't. Style guides are not enforced. Templates are optional. The next
developer to write a feature does it their own way, in a hurry, with good
intentions.

The deeper problem is that **the structure of documentation is detached from
the code that should produce it.** A style guide lives in one place; features
live in another. There is no mechanism to connect them.

---

## Specification shape as an inheritable contract

`libspec` features are Python classes. Python classes support inheritance. This
turns out to be exactly the right tool for the problem.

Consider `libspec-diataxis`:

```python
# libspec/diataxis.py  (published as the libspec-diataxis package)

from libspec import Feature, UnimplementedMethodError

class Diataxis(Feature):
    """
    Feature Specification: {{feature_name}}

    {{description}}

    ## Tutorial
    {{tutorial}}

    ## How-to Guide
    {{how_to}}

    ## Reference
    {{reference}}

    ## Explanation
    {{explanation}}
    """

    def tutorial(self):    raise UnimplementedMethodError()
    def how_to(self):      raise UnimplementedMethodError()
    def reference(self):   raise UnimplementedMethodError()
    def explanation(self): raise UnimplementedMethodError()
```

`Diataxis` is not a documentation template. It is a **specification contract**.
Any class that inherits it must implement all four quadrants or the
spec-generation step will raise `UnimplementedMethodError` — explicitly, at the
class and method that failed, not silently at runtime.

The contract is not optional. It is enforced by the same inheritance mechanism
that Python uses for abstract base classes — except it operates at the
*documentation level*, not the implementation level.

---

## Inheritance carries the contract through your entire hierarchy

The practical effect is significant. You inherit `Diataxis` once, at your
project's base class:

```python
# your project's spec/base.py
from libspec.diataxis import Diataxis

class Feature(Diataxis): pass
```

Every single feature class in your project now carries the Diataxis contract,
automatically, forever, without any per-feature configuration:

```python
class AuthenticationFlow(Feature): ...    # must implement all four quadrants
class CheckoutCart(Feature): ...          # must implement all four quadrants
class AwesomeNavBar(Feature): ...         # must implement all four quadrants
```

The structure of your documentation is no longer a convention to remember. It
is a structural property of your codebase, enforced by the compiler.

---

## Stacking contracts with multiple inheritance

Generic specs compose. A project base class can inherit from as many
specification contracts as makes sense for that project:

```python
from libspec import Feature
from libspec.diataxis import Diataxis
from libspec.conventioncommits import Commit

class MyFeature(Feature, Diataxis, Commit): pass
```

Now every feature in the project must satisfy all three contracts simultaneously:
the Diataxis four-quadrant documentation structure, the Conventional Commits
message format, and whatever `Feature` itself mandates. Each contract is defined
once, in its own library, maintained by whoever cares most about that concern.

This is the same composability that makes Python's mixin pattern powerful —
but applied to *specifications* rather than to implementation.

---

## What generic specs can encode

A generic spec can encode any specification structure that features or
requirements should share. Examples:

| Library | What it enforces |
|---------|-----------------|
| `libspec-diataxis` | All four Diátaxis documentation quadrants |
| `libspec-conventioncommits` | Conventional Commits–formatted change descriptions |
| `libspec-adr` | Architecture Decision Record fields (context, decision, consequences) |
| `libspec-openapi` | OpenAPI-compatible endpoint contracts |
| `libspec-a11y` | Accessibility requirements checklists |

Any cross-cutting concern that every feature should address — but that is
distinct from what any single feature *does* — is a candidate for a generic
spec library.

---

## The ecosystem effect

When `libspec-diataxis` is in wide use, something valuable happens at the
ecosystem level.

Every project using it speaks the same documentation language. Tooling can be
built that knows: *"any feature that inherits `Diataxis` has a `tutorial`,
`how_to`, `reference`, and `explanation`."* Documentation generators, agent
prompts, quality dashboards, and review checklists can all be written against
that guaranteed shape.

This is the same network effect that makes standard interfaces like
`collections.abc.Mapping` or `contextlib.AbstractContextManager` valuable: the
more widely they are adopted, the more tooling can be built around them.

Generic specs make that effect available at the *specification and documentation
level* — not just the API level.

---

## Summary

| Concept | What it means in practice |
|---------|--------------------------|
| **Generic spec** | A `libspec` class that defines *structure* rather than content |
| **Contract enforcement** | `UnimplementedMethodError` at spec-generation time — not a style guide to forget |
| **Inheritance propagation** | Inherit once at the base class; every downstream feature automatically complies |
| **Composability** | Stack multiple generic specs with multiple inheritance |
| **Ecosystem** | Shared spec shapes enable shared tooling, prompts, and review conventions |

The power of generic specs is that they turn documentation standards from
advisory suggestions into structural guarantees — and they do it using ordinary
Python inheritance, with no new syntax to learn and no new tool to run.
