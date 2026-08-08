"""
Specification for workspace .agents directory, skill installation, drift detection, and self-healing.
"""

from .err import Feat, Req


class AgentsDirectoryLayoutReq(Req):
    """
    The libspec platform recognizes the workspace `.agents/` directory as a primary
    customization root for AI agent skills and configuration.

    Path & Boundary Requirements:
    1. Discovery & Boundary Guards:
       - `.agents/` must be located directly at the project root (`os.path.join(project_root, ".agents")`).
       - If `.agents` exists as a regular file (instead of a directory) or is a dangling symlink,
         libspec must raise a clear `ValueError` diagnostic explaining the filesystem conflict.
       - Path traversal protection: Skill resolution must ensure symlinks do not escape the project boundary.

    2. Directory Hierarchy:
       - `.agents/skills/libspec/`: Canonical target directory for libspec agent workflow skills.
       - Backward Compatibility / Alias: Discovers legacy `.agents/skills/libspec-agent-workflow/` if present.
    """


class AgentsSkillValidationReq(Req):
    """
    Skill rendering, installation, and atomic file safety for `.agents`.

    Validation & File System Safety Rules:
    1. Atomic Installation:
       - Skill content must be rendered via Jinja2 templates and written to a process-isolated
         temporary file (e.g., `.agents/skills/libspec/TEMP_<pid>_SKILL.md`).
    2. Validation Enforcement:
       - The rendered content must be parsed using `SkillParser` to confirm valid YAML frontmatter
         (`name`, `description`) and markdown structure before replacing the active `SKILL.md`.
       - Rejects empty (0-byte) files, non-UTF-8 encodings, or invalid YAML metadata.
    3. Backup & Rollback:
       - If an existing `SKILL.md` is present, a backup (`SKILL.md.bak`) must be preserved prior to atomic rename.
       - If validation fails, the temporary file must be cleaned up, the original `SKILL.md` preserved,
         and a descriptive `ValueError` raised explaining the skill integrity failure.
    """


class AgentsSkillDriftDetectionReq(Req):
    """
    Drift detection for `.agents` skills on startup (CLI or MCP server initialization).

    Robustness & Comparison Rules:
    1. File Type Guard:
       - Verifies that `.agents/skills/libspec/SKILL.md` exists and is a regular file.
       - If `SKILL.md` is a directory or broken link, treats the skill state as drifted/corrupted.
    2. Normalized Comparison:
       - Normalizes line endings (LF vs CRLF) and trailing whitespace when comparing installed `SKILL.md`
         content against rendered template content to prevent false-positive drift warnings across platforms.
    3. Customization Protection:
       - If the installed `SKILL.md` contains the directive comment `libspec: disable-auto-heal`,
         drift detection marks the skill as customized and bypasses auto-healing to preserve manual edits.
    """


class AgentsSkillHealingFeat(Feat):
    """
    Auto-healing and graceful error recovery for `.agents` skills.

    Resiliency & Error Handling Rules:
    1. Auto-Healing Execution:
       - When `auto_heal` is enabled (default in MCP startup and CLI skill check), missing or drifted skills
         under `.agents/skills/libspec/` are automatically re-rendered and updated (unless user opt-out header is set).
    2. Permission & Read-Only Graceful Recovery:
       - If `.agents/` or its subdirectories have read-only permissions (`EACCES`/`EPERM`), healing must catch
         the exception, log a diagnostic warning explaining the permission failure, and allow the application
         to continue running rather than crashing the process.
    3. Concurrency Protection:
       - Process-isolated temporary files ensure multiple concurrent `libspec` invocations do not corrupt
         `SKILL.md` during simultaneous healing.
    """

    feature_name = "AgentsSkillHealingFeat"
