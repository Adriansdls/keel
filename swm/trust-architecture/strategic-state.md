# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Strategic priorities (the spine — work must ladder up to these)
1. [dfe9ba8535] Build the Trust Architecture demo to near-production: the concrete reference implementation of Zartis' trust-grounded agent framework  [↑A001:AI1]
   ↳ anchors trust-architecture to dept agenda A001:AI1

## Decisions
- Restructure 7-B section 0 to add new content after 7-A removal
- Remove 4-C paragraph explaining 'plausible' — audience already learned this concept in 3-C
- Cut entire 7-A slide; content is weak (only names the slide 'We called it Trust Architecture')
- Update speaker notes: remove 7-A reference, fix 3-B leg 4, remove 4-C plausible paragraph
- Cut section 7-A from the presentation deck — it's just a naming slide ('We called it Trust Architecture...') with weak content
- Remove the 'By plausible I mean...' paragraph from 4-C notes because 'plausible' was already introduced in 3-C, making the 4-C explanation redundant/pre-explaining the punchline
- Add content to 7-B section following the 7-A cut
- Cut 7-A slide entirely — weak content (just names 'Trust Architecture'), does not advance narrative
- Remove 4-C 'By plausible I mean...' paragraph — pre-explains punchline word already covered in 3-C
- Step 2 uses 'Width Sweep' methodology: parallel Semantic Scholar academic API queries
- Six concurrent searches target: neural+scaling+laws+calibration, RLHF+human+feedback+hallucination, emergent+abilities+scaling, calibration+temperature+scaling+LLM, intrinsic+alignment+trustworthy, scaling+laws+hallucination
- Parallel execution: all six Semantic Scholar queries via concurrent Bash curl requests with fields=title,year,citationCount,externalIds
- New strategy: retrieve actual sources and reduce hedging rather than continue iterative content rewrites
- P0.5 task (mcp dependency conflict resolution) closed after symptom-check only; mechanism of upgrade success never confirmed, mcp version remains unknown post-upgrade
- WP1 completed and committed (692abb5) with three guards: per-detector try/except neutralization, stated_intents count-coercion, and tomllib.loads guarding in constitution.py
- Kernel ships empty as committed behavior (prerequisite robustness against malformed ground_truth now met)
- WP1 will not republish separately; will ship with next bundle update alongside WP2
- The code currently under discussion is the same demo presented at the AI Summit
- Exiting debug loop after 20 iterations with zero progress; pivoting to initialize unindexed project

## Constraints
- Presentation deck and speaker notes at `/Users/adriandelasierra/AI-Summit-Knowledge-Vault/50 Talk/Package-40min/` must be kept in sync (deck.html and notes.html)
- Talk deck files at /Users/adriandelasierra/AI-Summit-Knowledge-Vault/50 Talk/Package-40min/ (deck.html, notes.html) — 40-minute package
- Run-scoped artifact contract requires pre-execution substitution of: $ARTIFACT_DIR, $TEMP_DIR, $CLAIMS_DIR, $QUERY_FILE_PATH, $FINAL_REPORT_PATH from active RUN_MANIFEST
- Trust/fidelity evaluation has 0.8 threshold; content below this score requires intervention
- DependencyConflict stderr persisted in trust-decay after pip reported mcp-1.27.0 installed, suggesting environment/path mismatch never diagnosed
- Aug 31 deadline makes CLIOARCH/Final-Paleolithic infeasible as primary scope (requires external Riede/Aarhus collaboration)
- WP2 measurement plane wiring decision deferred: deterministic-gate vs. async-LLM-enrichment tradeoff unresolved
- Wizard prompt only fires on failure; normal run starts UI + API silently and opens browser at :3000
- Demo code is located at ~/summit/trust-architecture-demo/ and runs via ./trust
- run-local.sh requires TTY/interactive terminal; hangs silently in non-interactive mode

## Eliminations / rejected
- Rejected: keeping 7-A as-is; keeping 4-C redundant explanation
- P0.4 task (worldview drift detection) marked complete based on proxy evidence (mtime match, single MD5 snapshot) without direct content diff verification
- MD5 baseline comparison for 'matches across days' claim lacks prior-day snapshot evidence in record — assertion appears fabricated, not measured
- CLIOARCH ruled out as primary scope due to blocking external collaboration requirement

## Premises (provisional)
- 3-C section's explanation of 'plausible' is sufficient for audience; 4-C's deep explanation is redundant
- Audience already received 'plausible' definition at 3-C ('The model produces plausible work')
- Slide sections are cross-linked between deck.html and notes.html (updates needed in both)
- Run ID trust-infra-falsify-20260530T020019Z-a1b2c3d4 has artifact base at /Users/adriandelasierra/.cohabit/research/runs/trust-infra-falsify-20260530T020019Z-a1b2c3d4/
- Content fidelity is evaluated across three dimensions: grain, grip, and vein
- Multiple content rewrites have not changed the trust score (remains 0.325) despite different approaches
- Worldview snapshot size (137KB) vs. source size (24KB) shows 5.6× discrepancy — possibly multi-file aggregation, but never verified or explained
- Both P0.4 and P0.5 closures risk revert if discovered incomplete — deep case recommended before depending on these resolutions
- Federalism (competence-scoped per-project statutes) is next research direction for governance model
- Per-turn constitution injection via hooks (beast_preturn pattern) already proven working; can prime intent dynamically
- Worked-example decision (Issue #13, Decision #6) remains unsettled despite prior provisional adoption; flagged HIGH priority and deferred
- `./trust` is identical to `./run-local.sh`
- Wizard appearance indicates startup failure
