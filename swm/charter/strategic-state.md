# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- GitHub remote will be added alongside existing Azure DevOps origin
- Force-push is planned to overwrite an empty init commit when establishing GitHub remote
- Mode changed from `strategic` to `advisory`; posture degradation no longer hard-blocks Charter operations
- Human-only gates (commit, push, deploy) now rely on Claude's own constitution enforcement rather than Charter's hook enforcement
- Charter continues to log every action and score rubrics; will not deny writes on stale checkpoints, but observability and scoring remain active
- Primary repair for projection_stale: run `charter render` (binary at ~/charter/.venv/bin/charter); it is whitelisted as a repair command and will not be hard-denied
- If `charter render` does not clear projection_stale, use whitelisted escape hatch `charter mode advisory` to downgrade Charter to non-blocking (advisory) mode, unblocking writes; strict mode can be re-enabled later
- Once charter unblocks (via render or advisory mode), immediately execute WP3: write 5 rubrics/*.yaml files (calibration data already mined), run unit suite plus live `claude -p` gate, update master plan
- Implement 4-phase sequence: Detection → Knowledge base → Guardian agent → Migration batching
- Detection phase: hook.py logs every skill/MCP touch, passes through, validates pattern coverage before LLM involvement
- Knowledge base ground truth derived from taxonomy.md + CLAUDE.md
- Guardian agent spawned by hook with --no-permission-prompts flag, receives request + session context via agenth
- Migration batching stores session state in /tmp/, buffers operations until threshold, evaluates as batch
- Definition of done: 5 approved operations, 1 reject, 1 redirect, 1 migration batch executed, full ledger trail, self-modification hard-blocked

## Constraints
- All repositories currently have Azure DevOps configured as the `origin` remote
- CLAUDE.md constitution principles remain the enforcement mechanism for human-only gates after Charter's hard-blocking is relaxed
- Deterministic charter score is 0.56, below required threshold of 0.75; projection_stale status actively blocks governed completion
- Charter assurance posture is degraded with projection_stale status; governed completion is currently blocked
- Implementation must follow single linear build sequence (phases are sequential, not parallel)
- Self-modification is hard-blocked in Guardian system
- Hook must always block the original request before Guardian processes it

## Premises (provisional)
- Projection staleness may stem from deeper ledger corruption; ledger.jsonl.corrupt.bak dated Jun 15 is evidence of prior ledger corruption and migration
- Pattern coverage validation is feasible in Detection phase before LLM involvement
- taxonomy.md + CLAUDE.md combination provides adequate ground truth for Guardian decision-making
