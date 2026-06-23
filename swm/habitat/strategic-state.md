# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Disable message masking to preserve prompt cache across turns (rationale: masking changed content every turn → cache miss every turn → expensive recompute) (tradeoff: caused model to imitate stub tokens in early sessions, now fixed)
- Implement tool denylist denying mcp_*, Workflow, Worktree tools — reduces 80 tools to 13–14 (rationale: unused tools are 47% of payload, cutting 81% tool content → ~38% overall payload reduction)
- Selective tool_result pruning for long sessions (>10 messages): stub old outputs with '[tool output — elided]' (rationale: tool results are 37% of payload in 315-msg session, safe because model never outputs this format)
- Compress tool descriptions to first sentence (~150 chars), preserve JSON schemas (rationale: model doesn't need verbose prose for correct schema interpretation; saves 46% of tool payload)
- Stabilize system-reminder turn counter: replace volatile exact numbers/timestamps with stable placeholders like 'N prior turn-events (last [ts])' (rationale: volatility invalidates cache every turn; placeholders preserve cache hits)
- Inject persistent cache control on stable system blocks — converts 5-min ephemeral TTL to 1-hr persistent (rationale: amortize write cost across sessions; saves $13.80–$124/month depending on session frequency)
- Verify SessionStart hooks across all settings files to test CLAUDE.md's claim of briefing injection at session start
- Check habitat plugin for briefing hook because no ra-pm SessionStart hook found in standard settings
- Read habitat's hooks.json to confirm what SessionStart actually invokes
- Agent-forge decoupled from habitat (T3, commit 8e4e874): observers inlined, outcome.align no longer a functional dependency, machine-root remains intact
- A2 (Track A item 2, ~95% complete) is a clean, committed checkpoint; can pause here before T7 or proceed with non-destructive parts only (extend comply, repoint agent new, remediate to builder)
- T3a/b (forge_gate + outcome_align edits to recognize zartis-forged agents) verified working with zero regression, ready to commit but currently uncommitted
- agent-forge will be moved to ~/.agent-forge.retired (reversible backup) not hard-deleted
- Plan number one is selected for execution
- T3a is verified functionally
- Process will pause at T3c awaiting user confirmation before proceeding with agent-forge retirement
- Habitat repo T6 changes (6 agents) will be committed when Adrian approves
- Commit current state as is for now, pending wire into proxy when other session ends
- Add fleet report to federation.py
- Competence typing implementation works correctly; court resolves curl grant authority as «federal_exclusive» per Art 155
- Hook conflicts resolve via shared execution (both run, not winner-takes-all) — established as the doctrinal fix
- ra-pm duplicate cost elevated to HIGH priority (8.3% budget impact)
- Constitution checking will use two layered approaches: #2 Haiku judge (primary) and #4 correction-mining (backstop)
- P002 and P004 classified as DIRECTIVE (observable-but-fallible) rather than ASPIRATIONAL, despite fuzziness
- All principles mapped to classification: 5 JUSTICIABLE (P001 security, P005 bounded-autonomy, ND1 claim-done, ND2 irreversible, ND3 bypass-governance); 3 DIRECTIVE (P002 no-human-framing, P003 LLM-first, P004 ownership); 0 ASPIRATIONAL

## Constraints
- Cost-benefit analysis for framework must exclude fixes that are specific to the user's personal computer setup or that the user implemented themselves (e.g., Fix 1 source)
- Prompt cache invalidates on any content change — even single-character changes in 21k-char blocks trigger expensive cache_write instead of cheap cache_read
- Tool schemas are structural contracts for correct model tool-calling; descriptions are prose reminders the model doesn't need
- Model never outputs tool_result blocks — only CC executes tools and receives results — so stubbing tool outputs is format-safe
- Investigation phase only—no writes, commits, or configuration changes were made
- Habitat plugin SessionStart hook implementation located at `/Users/adriandelasierra/.claude/plugins/cache/habitat/habitat/0.1.0/hooks/hooks.json`
- API tokens/keys from .env file were committed to version control
- No ra-pm SessionStart hook exists in /Users/adriandelasierra/.claude/settings.json or settings.local.json
- T7 is irreversible: deletes memory/scaffold/adopt subdirs, extends comply module — requires explicit confirmation before proceeding
- T3c (agent-forge retirement) is irreversible and gated on Adrian's explicit decision
- Selftest regression gate must pass before advancing beyond T3a
- T3c is the confirm-gated agent-forge retirement checkpoint
- Won't auto-commit T6 changes to 3 standalone project repos (cto-strategy, tostadito, finances) — they are Adrian's project repos, not CC OS repos
- Selftest regression gate must complete before T6 is confirmed complete
- OUTCOME: audit ra-pm decisions for ones a later decision contradicts but never explicitly supersedes
- Haiku judge must run async (flag+log+digest, no turn latency) and only in strategic gates to keep cost manageable
- New principles must be defined and documented in claude.md as part of the binding process
- 6 orphan authority rules are enforced but lack bound principles: force_push_default_branch, commit, push, deploy, external_send, spend_money
- Principles classified as: 5 JUSTICIABLE (P001, P005, ND1, ND2, ND3), 3 DIRECTIVE (P002, P003, P004), 0 ASPIRATIONAL
- 75% enforcement metric = 6/8 principles fully enforced, with P001 PARTIAL and P002 UNENFORCED
- 6 orphan authority rules (force_push_default_branch, commit, push, deploy, external_send, spend_money) are enforced but trace to no principle—enforcement with no law behind it
- P002/P004 classified as DIRECTIVE (observable-but-fallible) not ASPIRATIONAL—a constitutional judgment requiring ratification
- Coverage classifications in coverage.toml are tamper-pinned but reflect provisional initial judgments; ratification is Adrian's call via AMEND channel
- The 75% coverage metric = 6/8 principles fully enforced; P001 PARTIAL, P002 UNENFORCED; orphans + P002 are petition targets for habitat constitution digest
- Editing CLAUDE.md without ratification is detected and blocked; machine-root cannot be rewritten by the agent itself (bounded autonomy)

## Eliminations / rejected
- Full hooks.json content was not presented from Turn 10 Read operation; investigation stalled at that point
- SessionStart hook confirmed NOT in settings.json or settings.local.json
- SessionStart hook confirmed NOT implemented via ra-pm
- Receipt approach (#1) rejected: gameable (agent can cite fake blockers) and blind to silent shrink
- Parallelism approach (#3) rejected: too narrow and not load-bearing
- Proposal to defer work scope to later session explicitly rejected per session guidance — deferral on time/effort grounds lacks credible blocker (must be: human decision, missing credentials, irreversible/costly, or hard-constraint conflict)
- ASPIRATIONAL classification bucket intentionally empty—no principle deemed unobservable, nothing marked 'priming-only, human-audited'
- CLIOARCH ruled out as primary scope due to collaboration requirement and timeline conflict
- Remediator failed to validate build-agent skill; never pointed at ~/habitat/skills or never checked artifact layer
- Workflow, TeamCreate/TeamDelete, auth tools rejected as options
- Wire-masking approach was tried and failed—no longer viable
- Workflow, TeamCreate/TeamDelete, auth tools (~17k chars, 29 tools) identified as removable from DEFAULT_CORE—rarely/never needed in core CC sessions

## Premises (provisional)
- Experiment E validated 87–90% quality retention with tool_result pruning — model can answer factual questions correctly from summaries
- Turn counter stabilization test showed model produces equivalent-quality responses with stable vs. volatile counter values
- Session frequency varies 2–10 times per hour; persistent cache amortizes best at higher frequency
- CLAUDE.md claims briefing injection occurs at session start, but visible settings.json contains no SessionStart hooks
- Habitat plugin hypothesized to provide SessionStart hook not found in standard settings.json/settings.local.json
- CLAUDE.md claims ra_pm_brief observer on UserPromptSubmit hook injects briefing once per session on first prompt
- Habitat plugin at /Users/adriandelasierra/.claude/plugins/cache/habitat/habitat/0.1.0/ is hypothesized as the source of the SessionStart hook
- Agent-forge was a deeper coupling than initially planned (functional call, not just file read) and has now been cleanly ported
- User has untracked proxy/hook/federation work in flight while A2 work is in committed state — timing sensitive for T7 destructive ops
- codebase-researcher is agent-forge's only real agent; retiring agent-forge orphans its continuity brief until re-forged via builder
- zartis-forged agents are now canonical (forge_gate briefs them); agent-forge agents still briefed = no regression during transition
- Can use Python code to derive/generalize by comparing against available tools in target project and creating a score (unconfirmed approach)
- Presupuesto view reveals 163k chars of unbudgeted allocations across 28 jurisdictions — a material visibility/governance gap
- ND2 'irreversible' conceptually covers the 6 orphan rules, but none has explicit principle binding
- Empty ASPIRATIONAL bucket indicates either all declared principles are observable, or a truly-unobservable principle remains unarticulated
- Constitutional judgments in coverage.toml are provisional and require Adrian's ratification via AMEND channel
- ND2 'irreversible' covers orphans conceptually, but none is explicitly bound to it
- machine-root is the single source of truth; live prose CLAUDE.md sections are generated from it during constitution_sync
- habitat constitution digest mines drift and coverage gaps to seed amendment petitions for ratification, but agent autonomy is bounded to prevent self-rewriting
- Constitution coverage currently at 75% enforced; P002 (no-human-framing) is flagged as UNENFORCED, P001 (security) is PARTIAL, with 6 orphan authority rules identified
- skills2 is the canonical raising-agents framework example with no runtime conflicts with global hooks
- Neanderthal–carnivore topic has draft and available gold standards; aligns with Lucía's expertise
- Relevant papers in citation network are densely linked to each other; junk papers only weakly linked to them
- Reliability gap exists between citation-density thresholds where junk breaks off versus where relevant cluster itself breaks apart
- Gold-standard expert reading lists exist for known-answer validation topics
