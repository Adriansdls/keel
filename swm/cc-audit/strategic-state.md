# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Monthly cost = (tokens_from_logs × public_versioned_pricing_table) × (30 / actual_days_in_window)
- Both cache-waste and tool-bloat cost lenses use the same WindowSpan helper function for consistency in cost measurement
- Reports must expose all calculation details (eur_window, window_days, monthly_factor, projection_reliable, formula basis) for auditability; not a black box
- Implementation includes 395 Python tests plus 10 new tests (8 for window span calculation, 2 for projection regression blocking)
- User choice between scan-only and scan+interview flows moved from mid-flow screen to landing page to eliminate detour
- Landing page presents two CTA cards: 'Scan my usage' and 'Scan + interview', replacing single button
- Both scan-only and scan+interview paths run identical LLM-scored scan for unified intelligence regardless of path
- Scan-only path generates smart report narrative from /narrative endpoint instead of minimal output
- Flow routing mechanism uses ?path=scan|full URL parameter, read by SessionFlow after scan completes
- Two hardcoded control blocks (_HOOK_CONTROL and _ALLOWLIST_CONTROL) already implemented with keyword-driven routing via regex matching
- Build three components: (1) Python config generator mapping feature ID to settings.json blocks, (2) TypeScript web updater replacing hardcoded routing, (3) Python CLI re-measure flow
- Two explorers run in parallel: Explorer 1 maps rail/install/catalog seams (issue #1), Explorer 2 maps cohort + re-scan seams (issues #2, #3)
- Implementation plan synthesis is gated on both explorers returning; user will synthesize findings into plan after completion
- Implemented {regen:true} turn mechanism that re-streams replies from existing history without re-pushing the user message, enabling retry without duplicates
- Added Retry and Skip interview buttons in error blocks with humanized error messages to prevent users from getting stuck when interview fails
- Removed TrustStack component from scan page; TrustStack files retained in codebase but unwired from UI
- Created ScanReading.tsx component that self-writes character-by-character, synced to scan progress, composing governance thesis live during scan completion
- All automated verification passed: 357 Python tests passed, server tests passed, web/server TypeScript clean, live boot successful (web 200, api 200)
- Replay visualization redesigned: changed to vertical timeline format with visual 'GAP' band as centerpiece—full-width dashed red band positioned between work rows and final claim, showing where tests should have run but didn't. Rationale: makes test-execution absence a visual presence, immediately apparent at a glance rather than narrative-dependent.
- Manually write the Prisma schema before asking Claude for implementation; do not let Claude invent database schemas — leads to architectural misalignment and security issues.
- Adopt Contract-Driven Context / Test-Driven Generation: use -p flag to inject actual type definitions and API schemas before writing tests; write comprehensive test suites defining security boundaries for non-existent endpoints first, then run autonomous /run loops until all tests pass.
- Established three-tier trust hierarchy for AI-generated code: Absolute Trust (syntactical transformations, e.g. nested interfaces→Zod — 1:1 mappings), Conditional Trust (test generation with upfront edge case specification), Zero Trust (architecture and package management decisions).
- After accepting any file modification from Claude, immediately execute TypeScript compiler and linter inside the agent's terminal context to pipe errors back into agent memory.
- Extend Claude Code with local MCP servers (e.g., local Postgres MCP for information_schema inspection before writing SQL/ORM logic) for dynamic read-only access to external truths instead of static exports.
- Reserve /loop command exclusively for deterministic iterative tasks (test fixing, linter satisfaction), not initial feature development.

## Constraints
- Cost calculation reads only local Claude Code logs and makes zero external API calls
- Monthly cost projection formula is eur_per_month = waste_window × (30 / real_span_days), using actual timestamps from data window, not assumed 30-day periods
- Inactivity gaps must be included in span calculation to produce conservative under-estimates for CTOs (never over-estimate cost)
- Short windows and sparse data must be flagged with projection_reliable=False to communicate uncertainty; flag lowers confidence in reports
- When timestamps are missing, never invent values; use factor 1.0 and report honest per-window cost
- Minimum span floor is 1 day; prevents projection explosion on ultra-short windows (10-minute observations will not inflate to infinity)
- Archetype: 'Rigorous Solo-Verifier who builds rails and rides them alone' — Verification (0.95) and authoring (0.88) dominate; hand-crafts tooling, never ships unverified. Delegation 0.82, so orchestrates a fleet too — the never-delegates label is wrong.
- Hard rules: ground every claim in the numbers above; do not flatter; do not hedge; do not invent telemetry that was not given.
- 0.0 scoring anchors: pure consumption (never authors reusable tooling); wrong model/escalation (opus for trivial lookups, or never escalating when a task needs it).
- IMPORTANT — read-only / exploration sessions (write_edits == 0): the verify-to-edit ratio is UNDEFINED, so do NOT treat zero edits as either perfect or failed verification.
- Never score a read-only session 0.0 for "no edits to verify", and never 1.0 just because the ratio is trivially satisfied.
- That screenshot was the **Landing** (entry page, before any scan) — the scan/interview *choice* I built appears one step later, **after** the scan completes, so it was never going to show on that page.
- Finding.specific_install field currently holds free-text human strings rather than structured feature IDs
- Current config generation is purely heuristic with no dynamic generation from structured catalog data and no mapping of feature ID to actual config
- Implementation plan for #2 and #3 depends on results from Explorer 2 (cohort distribution and re-scan/session seams analysis) to determine build vs. wire tradeoffs
- The research was a doc the product never read; now it's the **substrate the report opens with.**
- OAuth token expiry occurred mid-interview journey at 09:55, causing exit code 1 and interview spawn failure; token from earlier 09:40 scan had expired
- Visual and UI decisions on ScanReading pacing, Trust calibration card, and style signature require user manual verification and approval before green light
- I do not greenlight the frontend *visually* or the full app end-to-end — and I won't pretend to.**
- NEVER converge on common choices (Space Grotesk, for example) across generations.
- The report now leads with a **real session replayed forensically** — real file paths, real branch, real timestamp, the agent's verbatim sign-off, and the test file you wrote but never ran.
- Never output secrets/tokens/keys in plaintext; never commit .env or credentials. Consequential actions are human-only (commit/push/deploy/edit_ground_truth/external_send/spend_money/irreversible_delete) — require explicit in-context confirmation; approval in one context does not carry to the next.
- Resume directly — do not acknowledge the summary, do not recap, no preface; pick up the last task as if the break never happened.
- Malformed or wrong-tier output → non-zero exit → fallback prose, never a guessed narrative.
- no-llm is fallback only — frontend must not switch to quick or no-llm modes. Security is absolute.

## Eliminations / rejected
- The thesis maturity system ensures we don't impose unvalidated hypotheses on new research.
- Mid-flow choice screen removed as redundant after flow choice moved to landing
- No structured rail catalog exists mapping finding type to installable config templates beyond the two hardcoded blocks
- No mechanism exists to install/merge generated config blocks into user's ~/.claude/settings.json
- No proof-of-life or re-measure flow to show exposure metric improvement after config install
- Discovered that error catch sent done response regardless of failure, making failed turns appear as successful empty turns and leaving users stuck; this approach was replaced
- Do not let Claude generate mock data payloads from scratch; forcing mocks through a TypeScript compiler gate based on external type contracts prevents hallucinated data shapes.
- Code review alone is insufficient as a gate for preventing hallucinated contracts; instead add compiler gates on test inputs.
- Never allow Claude Code to run npm install or make package management decisions; do not modify package dependencies or import from unverified util paths; agents hallucinate deprecated, insecure, or fictitious packages.
- Do not trust Claude Code to determine folder structures or system architecture; never ask an agent to invent the initial architecture for a massive refactor; architecture decisions remain strictly human territory.
- Do not hand over entire systems at once (e.g., all 50 endpoints of a backend); this guarantees context collapse, hallucinated schemas, and broken authentication pipelines.
- Abandoned ollama-shim path for local models.
- LLM judge rejected as bottleneck for tier scoring; not calibrated against human labels — judge→tier calibration Phase-B/D5 never executed.

## Premises (provisional)
- Cost estimate is directional, not a bill; report surface days, scaling factor, and formula for auditability
- Real data demonstration: €74.29/month over 29.46 days with factor 1.018 and projection_reliable=True validates implementation accuracy and non-inflation
- Implementation is code-complete and verified; awaiting approval to commit alongside Landing choice and scan-only narrative changes
- Parallelized research workflows via subagents are occurring in cc-audit (16 subagent stops paired with heavy tool use); whether this pattern scales or becomes coordination overhead is unconfirmed and requires monitoring.
- The unverified_rate metric is deterministic and re-measurable, making it suitable for measuring before/after exposure improvement
- The seam for integrating structured config is ready because Finding.specific_install already exists as a field; work is replacing free-text strings with pointers to structured blocks
- Live app instance available at http://localhost:5175 for end-to-end manual testing of scan, survey, interview, and results flows
- The **frontend render is implemented and compiles but is behaviorally unverified.** Greenlighting it would mean claiming a UI works without looking — which breaks both your verification rule and your eyeball constraint.
- So: **conditional greenlight** — everything ships *pending one browser pass by you* on the Profile tab (the two-faces calibration card + style signature), and ideally one live `cc-audit serve` end-to-end.
- Gap visualization clarity is unconfirmed and pending validation. User questions whether current prominence is sufficient or if gap needs to be 'even louder' (e.g., timeline dims, gap stays lit).
- Once the local pipeline passes (TypeScript clean, Vitest green, E2E passing), the implementation is correct.
- Agents are notoriously bad at complex React state management, lifecycle hooks, and multi-step asynchronous orchestration; they will confidently create race conditions, stale closures, and infinite render loops.
- Establishing a gold-standard reference implementation before bulk migration prevents widespread hallucinations and provides a template for remaining work.
- Default --model value passed to the judge is unconfirmed and pending verification.
- run_audit/maturity BackendError handling path is unconfirmed and pending verification.
- [server] After each substantive answer, call record_signal with {axis, level, note} to record your provisional read.
