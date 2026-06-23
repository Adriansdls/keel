# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Do NOT claim percolation threshold separation as novel theorem — it likely reduces to stochastic block model / community detection (planted-dense-subgraph recovery theory), not new math
- Plant novelty flag on framing + empirical demonstration + domain boundary, not mathematical innovation — method-application + empirical validation + domain boundary, using SBM/percolation as rigor scaffold
- Genuine novel contribution is the failure finding: archaeology's citation graph fragments by language/tradition, so apparent 'geographic gaps' are retrieval artifacts, not ground truth
- Safer novelty pillar is the whole-system thesis (boundary-condition framework + observable/interpreted extraction + descriptive-only synthesis + IOV-as-metadata) rather than any single percolation-based component
- Validation approach: test on topics with known expert-verified reading lists to confirm the reliability gap exists before claiming the method generalizes
- Design: don't build a second kernel-maintained list; use existing ~/.ra/projects.yaml + ~/.ra/thesis/<id>.yaml + .ra-project.yaml markers (owned by ra-pm)
- Skills can have agentic steps via caged agency (kind=agentic + schema + invariants)
- Strategic-memory is a skill (not an agent); confirmed by 25-assertion transition-evaluation test
- Three work buckets committed: A (skills2 core refactor: merge spec_additions.py, dash-hook→swm_events, transition-eval gate), B (engine: execution_model+kind in WP0, dual executors, audit primitives, event-skill WP3), C (SWM hygiene: fact_list.json invariants, correct 2 answered premises)
- Do NOT implement skills2 in this context
- ra-pm is authoritative record for decision state; SWM's auto-capture prematurely flagged the decision as 'decided' when it remains reopened and provisional
- skills2 bundle will NOT be uninstalled; relationship to existing code will be documented instead
- Paper 2 primary worked-example: Neanderthal–carnivore (feasible by Aug 31); CLIOARCH/Final-Palaeolithic reserved as post-submission high-credibility stretch validation

## Constraints
- Must validate novelty claims against three literatures before committing: scientometrics (percolation/community structure for corpus delineation), SR methodology (citation-search recall + stopping rules), community detection (detectability thresholds)
- The citation-network method only works if measurable link-density separation exists between relevant and irrelevant papers; no safe parameter setting if they break apart together
- Two live items on the current store, separate from this design: the premise-check is **⛔ blocking** (`ca7abc466724` flagged invalid) and the pre-fix leaks (`You never modify the kernel.`, etc.) are still rendered.
- One live note: the injected block right now still shows pre-fix leaks (`You never modify the kernel.`, the compound worked-example line, a stale "settled premise" ⛔).
- When either cap is exceeded → `over_budget()` True → **Sonnet consolidation** merges/drops with judgment (never blind truncation; `render` just shows most-recent-first, capped).
- 3-axis audit physically cannot grade hooks—only evaluates agent responses; WP3 must use transition-evals, not trust-anchoring
- Extractor leaking non-strategic items into fact_list.json: markdown header misclassified as constraint, ephemeral actions as decisions
- **Descriptive-only synthesis (a safety rule).** The machine only does arithmetic on retrieved evidence (counts, maps, networks); it never writes interpretation, even with RAG.
- Before any Paper 2 drafting, the worked-example decision must be formally revisited and settled (currently blocked)
- **Observable/interpreted separation under "retroactive legibility"** — extract the distinction the source text was never written to carry; conservative extraction + **two confidence fields** (source-legibility + extraction-accuracy).
- **The build map is a roadmap; the paper is a slice — do not scope-creep into the full system.**

## Eliminations / rejected
- CLIOARCH/Final-Paleolithic ruled out as primary scope (requires Riede/Aarhus collaboration, infeasible for Aug 31 deadline)

## Premises (provisional)
- Prior-art search has not been run — critical blocker for any novelty claim
- Relevant papers in a citation network are densely linked to each other; junk papers are only weakly linked to them
- A reliability gap exists between the citation-density threshold where junk breaks off the network and where the relevant cluster itself breaks apart—wide enough to set parameters safely in the gap
- Gold-standard expert reading lists exist for known-answer validation topics
- Neanderthal–carnivore: draft exists, gold standards available, aligns with Lucía's expertise; CLIOARCH: cleanest ground truth but blocked by external collaboration need
- Worked-example decision (Issue #13, Decision #6) remains unsettled despite prior provisional adoption; marked HIGH priority, deferred
- skills2 is canonical raising-agents framework example; no runtime conflicts with global hooks
