import json
import os

from libspec.mcp_server import peek, search, symbols


def test_symbols_spec_py():
    """Verify we can list symbols in libspec/spec.py."""
    spec_py = os.path.abspath("libspec/spec.py")
    res_str = symbols(spec_py)
    res = json.loads(res_str)

    # We expect to find classes like 'Spec', 'Ctx'
    names = [item["name"] for item in res]
    assert "Spec" in names
    assert "Ctx" in names


def test_peek_ctx():
    """Verify we can peek at the Ctx class definition."""
    spec_py = os.path.abspath("libspec/spec.py")
    # Find Ctx line
    with open(spec_py) as f:
        lines = f.readlines()
        ctx_line = -1
        for i, line in enumerate(lines):
            if "class Ctx" in line:
                ctx_line = i
                break

    assert ctx_line != -1, "Could not find 'class Ctx' in spec.py"

    # Peek at the 'Ctx' word
    res_str = peek(spec_py, ctx_line, 6)
    res = json.loads(res_str)

    # We expect a definition pointing to the same file or nearby
    assert res.get("definition") is not None


def test_search_mcp():
    """Verify we can search for the McpServer class."""
    res_str = search("McpServer")
    res = json.loads(res_str)

    # We expect to find 'McpServer' class
    names = [item["name"] for item in res]
    assert "McpServer" in names
