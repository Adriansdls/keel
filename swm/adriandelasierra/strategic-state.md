# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Cache fix prioritized first (rank 0.91) because it has highest € return and requires only one config line; tool-trim savings compound only on stable prefix
- Verification installed as dependency anchor despite ranking third by score, because cache and scoping fixes are untrustworthy without a verification gate
- Profile tab layout: AITT tab nav, L3 badge card, 2-col radar + signal triangulation, axis breakdown bars, 2-col discrepancy finding cards
- Leverage & Cost tab layout: 'From L3 to L4' header, €220 red hero card, dark hope-governance callout, 2-col fix grid
- Questions tab uses AITT pattern: numbered priority actions, ranking rationale card, closing nudge card, download button
- Core reframe locked: implement runtime verification of agent-asserted completion claims — a monitor that fires any turn, re-executes cited evidence, never trusts assertion
- Interactive sessions must use evidence-based verification: agent cites evidence_refs (concrete artifact pointers), gate independently re-executes them (tests, reads, hash checks)
- Two distinct verification mechanisms needed: pre-committed DoD for autonomous pipelines vs. evidence-based verification for interactive sessions
- Daemon with 300s interval is backstop for indexing; skipped observers incur ≤5min delay, acceptable tradeoff for CPU sanity
- Team is committed to iterating until v1 is achieved
- V1 implementation follows a CTO strategy approach (rationale: works very well)
- Files will be built in parallel
- suit is the canonical base for cc-workshop-vault; cto-strategy adds no features over suit, only cosmetic string changes and prompt tuning for CTO context, making suit the preferred choice for customization
- cc-workshop-vault customization limited to: DOMAIN_PRIMER for CC workshop context, query classifier prompt reframed for 'Claude Code workshop participant', and two-layer content architecture; vault_graph.py, trust.py, trust scoring, provenance contracts, mesh scoring remain unchanged
- Build cc-workshop-vault, a suit instantiation for Claude Code workshops with shared content from zartis-academy-platform and per-workshop sessions from transcripts
- Vault has two corpus layers: shared (generic Claude Code patterns extracted from academy-platform) and session (per-workshop extracted from transcripts by date)
- Support two parallel delivery modes: local MCP (git clone → python setup.py) and hosted MCP remote (participants add endpoint to claude_desktop_config.json for zero local setup)
- Admin post-workshop workflow: copy transcript file to transcripts/ → run ingest_session.py → git push; participants pull and vault becomes live with new session content
- Seven-step build order: (1) fork suit and rename, (2) write Claude Code domain primer, (3) ingest_shared.py extracts academy-platform to vault/shared/, (4) ingest_session.py extracts transcripts to vault/sessions/<date>/, (5) patch MCP server for two-vault search, (6) write participant CLAUDE.md with zero-jargon instructions, (7) create eval set of 15 questions on shared content
- Product is cc-audit: a standalone package that scans real Claude Code usage and returns evidence-backed maturity reports plus specific fixes; positioned as consulting deliverable + showcase repo for client orgs
- ~/.claude/context-proxy/proxy.py is chosen as primary data source: wire-level chokepoint on every /v1/messages call, already 5.6G captured, shows tools offered vs. tools used, beats parsing 46K jsonl transcripts
- Five lenses operationalize CTO feedback: (1) features unused, (2) cost/time waste, (3) model-routing inefficiency, (4) authoring/leverage (repeated manual work → package), (5) integration dead-weight; each emits uniform Finding(score·evidence·action·install·why·savings)
- Architecture: four layers — capture/harvest (facts), judges (map-reduce via claude -p, agnostic), synthesis (verdicts), commander skill (agentic mirror, currently missing)
- rubrics/ asset: model-fit as versioned LLM rubrics — this is the LLM-first heart of the product, making it agentic-era groundbreaking vs. regex NLP
- catalog/ asset: every recommendation→named install+why; this is the coaching/client-facing function that differentiates as groundbreaking product, not a linter

## Constraints
- Verification sits at L2 — trusting model confidence rather than actual checks; telemetry measures L1.6 vs. self-reported L3.5
- 38% of state-changing sessions shipped mutations with zero verification evidence in trajectory
- Cache reuse at 12% — 40k input tokens recomputed every turn due to context mutations above cache breakpoint
- Only 0.6% of offered tools are actually used (158 offered per call, ~10 tools touched in busiest projects)
- AITT format must be used for UI components, particularly for the Questions tab with numbered priority actions
- Work architecture should prioritize parallelization opportunities rather than remain too vertical
- I never start a task without updating or creating a CLAUDE.md file in the root directory.
- I explicitly define the stack (e.g., "We use Next.js App Router, strict TypeScript, and Tailwind"), testing conventions, and specific anti-patterns (e.g., "Do not use React FC types").
- When Claude Code executes a task and proposes file modifications, I never blindly accept the changes.
- If I spot an error, I reject the diff immediately and provide a one-sentence correction (e.g., "Reject: Do not use lodash, use native array methods").
- I never ask an agent to invent the initial architecture for a massive refactor.
- Do not modify or rewrite the underlying Prisma database queries."
- I operate on a principle of **zero semantic trust**—meaning I never trust the agent's natural language explanation of what the code does—and rely exclusively on compiler signals and test execution.
- Do not modify package dependencies and do not import from unverified util paths."
- I never switch to my browser to click around or manually QA the UI until the static analysis passes.
- If tests do not exist for the newly generated code, the code does not exist to me.
- When I looked at the actual runtime error, the app was throwing a `TypeError: Cannot read properties of undefined (reading 'zipCode')`.
- Now, I absolutely never let Claude Code infer or generate mock data payloads from scratch.
- If TypeScript throws a type error on your mock data, you must fix the mock to match the schema, do not change the schema."*
- I do not let Claude invent the database schema or the API contracts.
- Do not write a single route without tenant isolation."*
- Do not stop until the suite is 100% green."*
- But passing tests do not guarantee secure code.
- I instruct Claude: *"Do not guess the database structure.
- Do not run individual test commands."*

## Eliminations / rejected
- Not doing work needing verification — extracting claims from source text.
- And I rejected its first instinct to run a smoke on seeded demo data and make up a verdict - that was a fabrication trap I caught and stopped.
- Pre-committed contract/DoD model rejected for interactive sessions: only viable for orchestrated pipelines with defined task boundaries; interactive sessions have dynamic scope, no clean boundaries, and multiple mid-session 'done' claims
- keel (memory module) and ra-pm are out of scope for cc-audit; kept for inform-only reference
- `charter render` is rejected as a proper solution; it papers over symptoms without addressing root cause and requires repeated execution
- Option B (request force-repair from attest project) was considered but deferred in favor of immediate truncation
- Option 2 (claude --dry CLI flag) not viable; CC CLI flags are fixed and require binary patching to inject custom ones
- Drop the `requester` field entirely.
- Wire-masking approach was tried and failed; no longer a viable strategy
- Sessions 952883c7 (June 14), 06fc98b6 (June 15), and early-June fragments are NOT the keel origin development session; verified as explanations or later architectural discussions only
- ra_inject_preview implementation and Investigate are test implementations for calling the new mcp, NOT the actual implementations used to build the system
- Organizing projects into folders like ~/projects/ or ~/work/ is a separate, unrelated problem from discipline/skill scoping. Deferred as a larger migration.
- Skills `fernando` and `build-agent` were deleted during the migration; no rationale provided
- daily-standup will be removed from global registry; it is a template/example in raising-agents/skills2/examples/, not a production skill
- forge-frontdoor entry will be removed from global registry
- Workflow, TeamCreate/TeamDelete, auth (~17k, 29 tools), and Zartis tools (~3k, 12 tools) removed from DEFAULT_CORE via denylist in proxy.py; rarely/never needed in core CC sessions

## Premises (provisional)
- Hooks, per-project MCP scoping, and memory files are structurally dark — no installed controls catch behavioral regression or unverified state changes
- Tier 2 to Tier 3 gap is not model capability but one hook, one scoping statute, and one verify step — none requiring refactor to install
- All three dashboard tabs (Profile, Leverage & Cost, Questions) are rendering correctly and functioning as specified
- So the signal was: the agent was treating unverified provenance as ground truth.
- Plans, recommendations, and explicitly unverified statements are not operational_claims.
- `skipDangerousModePermissionPrompt` only skips the startup warning dialog, not per-command permission prompts
- Interactive session tasks characteristically lack clean specs, start mid-conversation, morph scope during work, and see multiple independent 'done' claims
- Pending Tasks:
- The code now compiles; the actual end-to-end test is pending.
- **The one thing not closed:** actual Phase-B human labels.
- Academy curriculum (4 course tracks: next-fundamentals, nextgineer, nextgineer-ii, nextperts, architect modules) is locally cloned at /tmp/zartis-academy-platform/platform/src/content/ and ready for integration
- The Claude Code domain primer is identified as the key asset that defines card quality; this must be written with precision to control extraction output
- suit is a generic extraction framework using DOMAIN_PRIMER as the customization point; it extracts typed vault cards with types: vision, decision, principle, tension, open_question, assumption
- cto-strategy (also called local-agent-trust) is an existing suit instantiation for CTO domain and serves as reference implementation for this project
- User has previously built AI-Summit-Attendee-Vault using a similar pattern of extracting domain-specific vault content from an event
- 24-hour event log shows 44 SessionStart vs. 39 SessionEnd events—5 sessions are unclosed or stale, indicating a session lifecycle timing issue or incomplete cleanup.
- Permission/policy observer framework has reached convergence: auto_allow, zesm_pretool, policy_drift, and dcp_policy all fire at identical rates (548 each per 548 tool invocations), indicating mature synchronized policy enforcement.
- Over 24 hours, adriandelasierra project represents 754 of 1241 events (61%), while sentinel (184), cc-config-ui (113), charter (68), habitat (53) are significantly smaller—work heavily concentrated on primary project.
- This is explicitly an exploratory research task; full scope, module reuse, and adjacencies are not predetermined and must be discovered through mapping
- The proxy is the only place the 'tienes medio planeta conectado y no lo usas' gap (half-planet-connected-but-unused integration) is visible and measurable
- Charter will continue blocking inside CC sessions as long as SWM writes to CLAUDE.md each turn, creating an unbreakable staleness cycle
- After both patches, Guardian Phase 3 will read pass-through unchanged, while writes/moves to skills/MCPs spawn guardian agent evaluation, which blocks or executes appropriately
- Attest ledger corruption is the underlying issue causing charter to block sessions
- Running the 4-step Terminal process (hash computation, ledger.head update, attest migration, charter render) will fully unblock charter
- Two processes wrote simultaneously at record 179, creating a fork with records 180-181 sharing identical prev_hash (b32e7e176695), breaking the validation chain
