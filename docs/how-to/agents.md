# Integrating with LLM Coding Agents via MCP

`libspec` features a Model Context Protocol (MCP) server that exposes specification tools directly to LLM agents (such as Antigravity, Claude Desktop, Cursor, Cline, or Copilot). This allows the agent to fetch context, search spec components, view diffs, and inspect dependencies natively during a session.

---

## Supported Agents & Workspace `.agents/` Layout

`libspec` recognizes the project root `.agents/` directory as the primary workspace customization root for AI agent skills.

Supported target configurations:
*   `agents` (Standard `.agents/` workspace layout — auto-configured on `libspec init`)
*   `antigravity` (Google Antigravity IDE Agent)
*   `gemini` (Gemini CLI)
*   `claude` (Claude Desktop & Claude Code)
*   `copilot` (GitHub Copilot)
*   `opencode` (OpenCode Agent)
*   `codex` (Codex IDE)

---

## 1. Automated Configuration

When running `libspec init`, the `.agents/` workspace skills directory is created automatically.

To configure or re-install skills for specific coding assistants, use `agent-config` (or alias `mcp_agent`):

```bash
# List all supported agents
uv run libspec agent-config --list

# Scaffold/update .agents workspace skills
uv run libspec agent-config agents

# Configure specific agent integrations (e.g. Antigravity)
uv run libspec agent-config antigravity
```

This automated step:
1.  Locates your local virtual environment's `uv` executable path.
2.  Creates the canonical target directory `.agents/skills/libspec/`.
3.  Installs or updates **`SKILL.md`**, rendered via Jinja2 with atomicity and `SkillParser` validation.
4.  Preserves backward compatibility for legacy `.agents/skills/libspec-agent-workflow/` paths.

---

## 2. Skill Drift, Auto-Healing & Customization

LLM agent prompts require precise instruction schemas (skills). To prevent prompts from becoming outdated as `libspec` evolves:
*   On startup and CLI invocations (e.g., `libspec diff`), `libspec` scans your workspace's `.agents/` configuration.
*   If it detects a missing or modified `SKILL.md`, it automatically **auto-heals** the file in place by writing a process-isolated temporary file (`TEMP_<pid>_SKILL.md`), validating it, backing up the existing file to `SKILL.md.bak`, and atomically replacing it.
*   **Customization Opt-Out**: If you customize your `.agents/skills/libspec/SKILL.md`, include the directive `# libspec: disable-auto-heal` in the header. `libspec` will detect the directive and preserve your manual edits without overwriting them.

---

## 3. Manual Configuration

If your developer agent is not listed in the auto-config registry, you can configure it manually by pointing to the standard I/O command:

```json
{
  "mcpServers": {
    "libspec": {
      "command": "uv",
      "args": ["run", "libspec", "mcp"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

Ensure that your agent is run in the root of your workspace (the directory containing `.libspec/`).

---

## Available MCP Tools

Once connected, your coding agent gains access to the following tools:

| MCP Tool Name | Description |
|---|---|
| `mcp_libspec_search` | Search specification components and docstrings by query string. |
| `mcp_libspec_show_component` | View complete details (docstring, inheritance, claims) of a component. |
| `mcp_libspec_list_components` | List all components recorded inside a target snapshot. |
| `mcp_libspec_diff` | Diff live (pending) specs against historical snapshots or base branches (`libspec diff main`). |
| `mcp_libspec_list_snapshots` | List chronological snapshot history. |
| `mcp_libspec_declare_dependency` | Establish a logical dependency between components. |
| `mcp_libspec_list_dependencies` | View recorded component dependencies. |

> **Tip:** When developing on a feature branch with intermediate commits, pass the base branch target (e.g. `libspec diff main`) to track the cumulative specification delta across all commits.
