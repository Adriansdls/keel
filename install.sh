#!/usr/bin/env bash
# cowork — one-command installer
# Usage: bash install.sh
# Re-running is always safe (idempotent on every step).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COWORK_HOME="${COWORK_HOME:-$HOME/.cowork}"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
PACKAGES="$COWORK_HOME/packages"
VENV="$COWORK_HOME/.venv"

echo ""
echo "  Installing cowork..."
echo ""

# ── 1. Prerequisites ──────────────────────────────────────────────────────────

if ! command -v claude &>/dev/null; then
  echo "  ⚠  cowork needs Claude Code to be installed."
  echo "     Download it at: claude.ai/code"
  echo "     Once installed, run this script again."
  echo ""
  exit 1
fi

if ! python3 -c "import sys; assert sys.version_info >= (3,9)" 2>/dev/null; then
  echo "  ⚠  cowork needs Python 3.9 or newer."
  echo "     Download it at: python.org/downloads"
  echo ""
  exit 1
fi

# ── 2. Directory scaffold ─────────────────────────────────────────────────────

mkdir -p "$COWORK_HOME"/{packages,ra,swm,entropy,outcome-loop}
echo "  ✓ directories"

# ── 3. Python venv + deps ─────────────────────────────────────────────────────

if [ ! -f "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q --upgrade pip "mcp[cli]>=1.0" pydantic pyyaml
PYTHON="$VENV/bin/python"
echo "  ✓ python environment"

# ── 4. Copy packages ──────────────────────────────────────────────────────────

cp -r "$SCRIPT_DIR/shared"       "$PACKAGES/"
cp -r "$SCRIPT_DIR/ra-pm"        "$PACKAGES/"
cp -r "$SCRIPT_DIR/swm"          "$PACKAGES/"
cp -r "$SCRIPT_DIR/auto-capture"   "$PACKAGES/"
cp -r "$SCRIPT_DIR/entropy"        "$PACKAGES/"
cp -r "$SCRIPT_DIR/outcome-loop"   "$PACKAGES/"
# Remove pycache from copied packages
find "$PACKAGES" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
echo "  ✓ packages"

# ── 5. Write config.yaml (once — never overwritten) ──────────────────────────

if [ ! -f "$COWORK_HOME/config.yaml" ]; then
  COWORK_HOME="$COWORK_HOME" "$PYTHON" - <<PYEOF
import sys, os
sys.path.insert(0, "$PACKAGES")
os.environ["COWORK_HOME"] = "$COWORK_HOME"
from shared.store import write_default_config
write_default_config()
PYEOF
  echo "  ✓ config written"
else
  echo "  ✓ config exists (not overwritten)"
fi

# ── 6. Create Claude settings dir if needed ─────────────────────────────────

mkdir -p "$(dirname "$CLAUDE_SETTINGS")"
[ -f "$CLAUDE_SETTINGS" ] || echo "{}" > "$CLAUDE_SETTINGS"

# ── 6. Register MCP server ────────────────────────────────────────────────────

# Register ra-pm MCP in Claude Code settings.json (direct write — no CLI quirks)
"$PYTHON" - <<PYEOF
import json, os
from pathlib import Path

settings_path = Path("$CLAUDE_SETTINGS")
s = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.exists() else {}
s.setdefault("mcpServers", {})["ra-pm"] = {
    "command": "$VENV/bin/python",
    "args":    ["$PACKAGES/ra-pm/server.py"],
    "env":     {"COWORK_HOME": "$COWORK_HOME"},
}
tmp = settings_path.with_suffix(".tmp")
tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
import os as _os; _os.replace(tmp, settings_path)
print("  ✓ MCP server registered in Claude Code (ra-pm)")
PYEOF

# ── 7a. Register MCP in Claude desktop app (Claude Cowork) ───────────────────

DESKTOP_CFG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$DESKTOP_CFG" ]; then
  "$PYTHON" - <<PYEOF
import json, os
from pathlib import Path

cfg_path = Path("$DESKTOP_CFG")
cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
cfg.setdefault("mcpServers", {})["ra-pm"] = {
    "command": "$VENV/bin/python",
    "args":    ["$PACKAGES/ra-pm/server.py"],
    "env":     {"COWORK_HOME": "$COWORK_HOME"},
}
tmp = cfg_path.with_suffix(".tmp")
tmp.write_text(json.dumps(cfg, indent=4), encoding="utf-8")
import os as _os; _os.replace(tmp, cfg_path)
print("  ✓ MCP server registered in Claude Cowork (claude_desktop_config.json)")
PYEOF
else
  echo "  ✓ Claude desktop app not found — skipping Cowork registration"
fi

# ── 7. Register hooks ─────────────────────────────────────────────────────────

COWORK_HOME="$COWORK_HOME" "$PYTHON" - <<PYEOF
import json, os, sys
from pathlib import Path

settings_path = Path("$CLAUDE_SETTINGS")
packages     = Path("$PACKAGES")
venv_python  = Path("$VENV/bin/python")

# Map: event → list of (command, timeout)
HOOKS = {
    "UserPromptSubmit": [
        (str(venv_python) + " " + str(packages / "swm/inject.py"),        5),
    ],
    "Stop": [
        (str(venv_python) + " " + str(packages / "swm/capture.py"),       45),
        (str(venv_python) + " " + str(packages / "swm/premise_check.py"), 45),
        (str(venv_python) + " " + str(packages / "auto-capture/hook.py"), 45),
        (str(venv_python) + " " + str(packages / "entropy/hook.py"),          60),
        (str(venv_python) + " " + str(packages / "outcome-loop/hook.py"),     90),
    ],
    "PreCompact": [
        (str(venv_python) + " " + str(packages / "swm/pre_compact.py"),   30),
    ],
}

# Load or init settings.json
if settings_path.exists():
    s = json.loads(settings_path.read_text(encoding="utf-8"))
else:
    s = {}

hooks_cfg = s.setdefault("hooks", {})
added = 0

for event, entries in HOOKS.items():
    event_list = hooks_cfg.setdefault(event, [])
    # Collect all commands already registered for this event
    existing = {
        h.get("command", "")
        for entry in event_list
        for h in entry.get("hooks", [])
    }
    for cmd, timeout in entries:
        if cmd not in existing:
            event_list.append({
                "hooks": [{"type": "command", "command": cmd, "timeout": timeout}]
            })
            added += 1

# Atomic write
import tempfile
tmp = settings_path.with_suffix(".tmp")
tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
import os as _os
_os.replace(tmp, settings_path)
print(f"  ✓ {added} hook(s) registered")
PYEOF

# ── 8. Migrate ~/.ra/ if present ──────────────────────────────────────────────

if [ -d "$HOME/.ra" ]; then
  echo ""
  echo "  Found ~/.ra/ — migrating existing data..."
  COWORK_HOME="$COWORK_HOME" "$PYTHON" - <<PYEOF
import sys, os
sys.path.insert(0, "$PACKAGES")
os.environ["COWORK_HOME"] = "$COWORK_HOME"
from shared.store import migrate_from_legacy
from pathlib import Path
r = migrate_from_legacy(Path.home() / ".ra")
print(f"  ✓ {r.n_migrated} records migrated, {r.n_skipped} skipped")
if r.errors:
    print(f"  ⚠  {len(r.errors)} records could not be migrated (originals untouched in ~/.ra/)")
PYEOF
fi

# ── 9. Done ───────────────────────────────────────────────────────────────────

echo ""
echo "  ┌─────────────────────────────────────────────────────────┐"
echo "  │  cowork installed ✓                                     │"
echo "  │                                                         │"
echo "  │  Open Claude Code in any project.                       │"
echo "  │  cowork starts working automatically.                   │"
echo "  │                                                         │"
echo "  │  Your projects:  ~/.cowork/                             │"
echo "  │  Settings:       ~/.cowork/config.yaml                  │"
echo "  └─────────────────────────────────────────────────────────┘"
echo ""
