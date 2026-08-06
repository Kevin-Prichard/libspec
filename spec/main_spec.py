"""
Main spec.
"""

from libspec import Spec

from . import (
    app,
    cli,
    code_quality,
    colors,
    commands,
    core,
    diff,
    git_hooks,
    mcp,
    repl,
    store,
    types,
    utils,
)


class MainSpec(Spec):
    def modules(self):
        return [
            app,
            core,
            cli,
            diff,
            types,
            mcp,
            utils,
            store,
            repl,
            colors,
            git_hooks,
            code_quality,
            commands,
        ]
