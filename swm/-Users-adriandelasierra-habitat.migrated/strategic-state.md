# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Defer federalism design (competence-scoped per-project statutes) to future Claude Code session; continue current path; note in PM docs
- Machine-root (`habitat/agents_lib/machine-root/`) is the authoritative single source of truth (principles + authority + rubric + contract, hash-pinned, ratified)
- CLAUDE.md block is auto-compiled from machine-root, delineated with `<!-- BEGIN/END MACHINE CONSTITUTION -->` markers; human prose sections (identity/comms, Beast-operational, ra-pm) remain hand-authored and untouched
- Three closed loops: Compile (`habitat constitution render`), Sync-verify (`constitution_sync` at SessionStart), Behavior-enforce (`constitution` at Stop, `beast_audit`, `policy_drift`)
- Shipped and live on main (`f41a780`); backup at `~/.claude/CLAUDE.md.bak-pre-constitution-*`
- Cache 0.1.2 (live, verified) packages constitution_sync + kernel/constitution.py + machine-root; mode strategic
- Sync watcher verification passes (in sync) running cache against real file; version bump being committed
- Prose exists to steer intent proactively and cover behaviors that don't surface as blockable actions; enforcement alone leaves reasoning-style/judgment ungoverned and creates high friction
- Constitution (machine-root: structured, versioned, hash-pinned, enforced) becomes the single source of truth; hand-authored prose dies as source
- CLAUDE.md will be compiled/generated from constitution (auto-regenerated, kept in sync by drift detection), rather than hand-written
- Three-layer architecture: machine-root (source), generated CLAUDE.md (static projection), per-turn hook injection (dynamic projection)
- Will pursue research on federalism architecture if preliminary assessment confirms it makes sense and has grounding in existing principles
- Merged to main locally (fast-forward cad25d2 → 7ded7a1), left unrelated family-menu changes untouched

## Constraints
- Push to remote is blocked; upstream (origin/master) is gone/renamed and requires clarification before pushing outward-facing changes
- Claude Code only consumes CLAUDE.md as prompt text—that is the only native channel by which a file influences model intent
- Hooks/enforcement layer operates on actions/outputs at/after decision points, not on model intent (reactive, not proactive)
- CLAUDE.md block primes intent (only proactive channel); hooks enforce mechanically-detectable subset (claim-done evidence, secrets, authority); purely-internal reasoning can't be verified—rides on priming alone (property of harness, not closable)
- Plugin `0.1.2` requires restart to apply; loads in next Claude Code session, not current

## Eliminations / rejected
- Weak hand-authored prose as the governing source is eliminated; a CLAUDE.md may exist but only as a faithful generated mirror with no independent impact

## Premises (provisional)
- Federalism-based governance model (constitution at top binding all, autonomous communities/projects with bounded autonomy) could structure Claude Code projects
- Per-turn constitution injection via hooks (beast_preturn pattern) already works and can prime intent dynamically
- Federalism (competence-scoped per-project statutes) is the next research direction, captured in ra-pm
