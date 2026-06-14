#!/usr/bin/env bash
# cowork — uninstaller
# Removes hooks and MCP registration. Leaves ~/.cowork/ data intact.
# Pass --purge to also delete all cowork data.

set -euo pipefail

COWORK_HOME="${COWORK_HOME:-$HOME/.cowork}"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
PURGE=false

for arg in "$@"; do
  [ "$arg" = "--purge" ] && PURGE=true
done

echo ""
echo "  Removing cowork..."
echo ""

# ── Remove hooks from settings.json ──────────────────────────────────────────

if [ -f "$CLAUDE_SETTINGS" ]; then
  python3 - <<PYEOF
import json, os
from pathlib import Path

settings_path = Path("$CLAUDE_SETTINGS")
s = json.loads(settings_path.read_text(encoding="utf-8"))
hooks_cfg = s.get("hooks", {})
removed = 0

for event, entries in hooks_cfg.items():
    before = len(entries)
    # Keep entries that have NO cowork commands
    hooks_cfg[event] = [
        entry for entry in entries
        if not any(
            "$COWORK_HOME/packages" in h.get("command", "")
            for h in entry.get("hooks", [])
        )
    ]
    removed += before - len(hooks_cfg[event])

# Clean up empty event lists
hooks_cfg = {k: v for k, v in hooks_cfg.items() if v}
s["hooks"] = hooks_cfg

tmp = settings_path.with_suffix(".tmp")
tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
os.replace(tmp, settings_path)
print(f"  ✓ {removed} hook entry/entries removed from settings.json")
PYEOF
else
  echo "  ✓ no settings.json found — nothing to remove"
fi

# ── Remove MCP server ─────────────────────────────────────────────────────────

if claude mcp remove ra-pm 2>/dev/null; then
  echo "  ✓ MCP server removed (ra-pm)"
else
  echo "  ✓ ra-pm MCP was not registered"
fi

# ── Purge data (opt-in) ───────────────────────────────────────────────────────

if [ "$PURGE" = true ]; then
  rm -rf "$COWORK_HOME"
  echo "  ✓ ~/.cowork/ deleted"
else
  echo ""
  echo "  Your data is still at: $COWORK_HOME"
  echo "  Delete it manually if you want:  rm -rf $COWORK_HOME"
fi

echo ""
echo "  cowork removed. Restart Claude Code to apply."
echo ""
