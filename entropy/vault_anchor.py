"""vault_anchor — check whether projects are anchored to a strategy vault.

Optional: if no vault_path is configured in ~/.cowork/config.yaml,
unanchored() returns [] and the metric is silently skipped.

Configure by adding to config.yaml:
  vault_path: ~/my-strategy-vault    # path to a dir of .md strategy cards
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.store import load_config, load_projects


def _vault_path() -> Path | None:
    cfg = load_config()
    vp = cfg.vault_path
    return Path(vp).expanduser().resolve() if vp else None


def unanchored() -> list[str]:
    """
    Return project ids with no corresponding strategy card in the vault.
    If vault is not configured, returns [] — metric is skipped, not broken.
    """
    vault = _vault_path()
    if vault is None or not vault.exists():
        return []  # vault not configured — no anchoring checks

    # Collect vault card titles (stems of .md files)
    card_names = {p.stem.lower() for p in vault.glob("**/*.md")}
    if not card_names:
        return []

    projects = load_projects()
    unanchored_ids: list[str] = []
    for p in projects:
        # A project is anchored if its id or name appears in any card stem
        pid_lower = p.id.lower()
        name_lower = (p.name or "").lower().replace(" ", "-")
        if not any(pid_lower in c or name_lower in c for c in card_names):
            unanchored_ids.append(p.id)

    return unanchored_ids
