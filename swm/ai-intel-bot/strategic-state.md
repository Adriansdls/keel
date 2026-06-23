# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Configure osxkeychain as global git credential helper with credential."https://dev.azure.com".useHttpPath=true for persistent Azure DevOps authentication
- Update `.env.example` in `/Users/adriandelasierra/ai-intel-bot/` to reference Azure DevOps vault URL instead of GitHub vault URL
- Create `/Users/adriandelasierra/ai-intel-bot/azure-pipelines.yml` with trigger on main branch pushes for optional CI/CD auto-deploy
- Sentinel architecture validated against the ephemeral-worker + trigger convergence pattern
- Event-based triggers and supervisor daemon for observability not yet implemented
- Anthropic shipped Dreaming (inter-session pattern extraction and preloading) as production feature in Claude May 2026, independently validating Sentinel's EVOLVE architecture at production scale
- ACID queue uses file-based coordination primitives (State-Flag, Event-Signal, Threshold-Trigger) matching stigmergy pattern from arXiv 2604.03997 and Physarum polycephalum; biologically-principled, not a workaround
- 5th trigger pattern validated via OpenCode Telegram bot: long-poll external API → localhost agent; adapted as Telegram → enqueue-task.sh → ACID queue, with human interrupt latency = next session boundary
- value-critic (BloodHound Phase 2 analyst) requires code-enforced harness implementation, not prose; decision justified by: multi-step analytical workflow (5 frameworks), judgment-driven assessment, reasoning over knowledge base (inventory markdown + JSON), and consequential output guiding configuration decisions. Counterweight role implies trust rubric needed for authority to critique other analysts.
- Ralph upgrade will use decision:block + additionalContext pattern in ralph-stop-hook.sh lines 103-143
- Recall fix will target AND-conjunction root cause with maximum 2 terms and exact tag strings, expecting improvement from 67% to 70-80% hit rate
- Sentinel will operate as Agent Teams teammate using peer-to-peer mailbox (CC v2.1.32+), replacing standalone daemon architecture
- Narrow+deep beats wide+shallow: principle validated by production; integration breadth creates failure surface; Sentinel's focused scope is a safety property
- Outcomes API and sentinel-reviewer are distinct and must coexist: Outcomes provides real-time retry-loop gate during execution; sentinel-reviewer is post-hoc longitudinal auditor after session completion
- Use decision:block + additionalContext for in-session task chaining instead of subprocess spawning.
- Replace SENTINEL_RALPH_ACTIVE env var guard with status-based filtering (queued → claimed → completed task transitions).
- H28 signal identified as worth pursuing in ACID queue semantics research
- Implement two-speed execution: within-session rapid + cross-session slow evolution (cohabit/EVOLVE)
- Agent graduation should measure 3-day survival rate (0.8–1.0 churn) rather than cycle count

## Constraints
- Batch-driven execution dominates: Sentinel 90/133 events in 24h with 59 pre-tool and 57 post-tool governance checks
- Live-SWE-agent within-session self-modification requires sandboxed container and audit logging
- Anthropic subscription tier must be confirmed by June 15, 2026; do not wait for email notification
- Azure access tokens expire; persistent git authentication mechanism required
- Dreams API form submission needs clarification: confirm whether 'Dreams API' form = Dreaming managed service before submitting
- STRUCTURAL SIGNALS (ground truth from tool call log — these dims are computed deterministically; do NOT override):
- Event-based triggers and supervisor daemon for observability not yet implemented
- Current architecture may not scale if event density doubles from baseline
- Memory poisoning cascades across sessions: finding from Day 3 redirected research on Day 30; sources field must be treated as security perimeter, not optional metadata
- Dreams API access is gated; requires form submission at claude.com/form/claude-managed-agents; Sessions and Outcomes APIs are open beta as of April-May 2026
- Sentinel implements only 1 of 4 Cursor Automations triggers (supports time-based, codebase change, Slack/incident, test failure; 3 remain unimplemented)
- Sentinel Ralph runs in non-interactive mode (claude -p), so any in-session chaining mechanism must work within this constraint.
- Missing implementation: event-based triggers + supervisor daemon for observability
- Daily execution window: 120 minutes to complete 8 tasks on day 41 (2026-06-16)

## Eliminations / rejected
- GitHub is not required for any deployment path; Modal deployment is completely independent and works 100% from local machine or Azure Pipeline
- Option A (non-blocking additionalContext without decision:block) rejected in favor of Option B.

## Premises (provisional)
- Devin architecture: fresh Linux VM per task, 89% self-generated code, sub-agents for planning/execution/verification, multi-model routing (not provider-locked)
- Human attention is the bottleneck, not AI capability
- Claude Code Agent Teams architecture: locked system prompt/model/permissions per specialist; supervisor daemon persists after terminal closure ('Claude living on the machine')
- Devin, Cursor, and Copilot independently converged on ephemeral worker + trigger system + PR-gated output architecture
- Always-on behavior created by trigger density, not persistent processes alone; Sentinel architecture validated against this pattern
- TIDE baseline established: 0.000 loop rate across 45 unique tasks with no looping detected
- Living-organism and sentinel drove 196 events across 8 sessions, with ~85 tool invocations distributed between organism.py/vitals.py edits, launchd config updates, and pending genome mutations in JSON state.
- Policy friction not blocking forward momentum: dod-test climbing to 40 events while allowlist enforcement (59 events each for auto_allow, policy_drift, dcp_policy) remains steady
- Cursor Automations supports 4-trigger taxonomy (time-based, codebase change, Slack/incident, test failure); Sentinel currently implements only 1 of 4
- 3.7k event/day baseline is provisional; behavior under concurrent multi-agent load is unconfirmed
- Governance system operates actively (policy triggers fire consistently: auto_allow, policy_drift, dcp_policy each 553 times) without restricting forward momentum
- ACID queue semantics is genuinely novel territory with no prior findings in the codebase
- Dreams API cost estimate must be obtained before commitment; enables multi-session synthesis (100 vs 1) and semantically safer operations than EVOLVE, but introduces per-token billing
- decision:block on Stop hooks works in -p mode per official Claude Code docs and v2.1.172 release notes (June 2026).
- Day 40 Sentinel finding identified decision:block + additionalContext as the pattern for Ralph in-session chaining.
- Sentinel daily operations involve coordination with 4 agents; system currently waiting for their execution
