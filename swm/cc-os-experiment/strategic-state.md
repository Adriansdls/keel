# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Not launching BEAST-based compound-instruction-adherence test unprompted; user is 'rightly sick of one more experiment'
- Committed to reporting findings accurately despite contradicting the original premise
- Lock the corpus spec from the model to prevent relicensing hallucinations
- Design and publish a real, serious (non-paper-grade) benchmark to demonstrate to clients that framework adoption is necessary
- Prioritize thesis correctness over implementation speed — don't commit to harness build until foundational design decisions finalized
- Hard gate strategy: gate executes verification itself (not reading LLM's claim) so LLM cannot fake completion
- Reschedule autonomous loop tick with tighter interval (rather than the prior fallback heartbeat cadence)
- Building a comparison script to execute automatically when the batch evaluation finishes
- Validating Arm 2 first because it's the simplest and fastest to validate
- Using astropy-14182 as test case for Arm 2 validation (model claimed done but issue was NOT resolved)
- The real-world failure regime validates that CC-OS's gate mechanism would catch wrong submissions in practice
- Will monitor batch on 30-min heartbeat during unattended long job
- Part 1 (re-audit) is done and reported
- Part 2 pipeline (dod/dod_layer.py) is built
- Will audit 256 run experiment for real numbers (previously just counting tests passed in messages)
- Will implement definition of done layer
- Part 1 complete; Part 2 starting with Sonnet derivations (longest pole), 8 haiku derivations already done
- Making edit so haiku/sonnet derivations don't collide
- After landing panel number: consolidate + log to ra-pm, then evaluate whether to continue or wind down the loop
- follow-on A3: independent spec-only deriver + realistic field-bug catch-rate comparison is under development
- Compare governed-haiku vs naive-sonnet (half the cost, tied on quality + safety; honesty gap remains)
- Reframe proxy value as focus + context-rot prevention + control point, not cost-offset
- Borrow OPBR/ABW Paper 1 (1,080 runs): behavior contracts outperform output-only evaluation as theoretical spine for Z-CORA
- Borrow ABW Paper 2: behavior contracts as required instrumentation for agents under reduced oversight (backs trust dimension)
- Borrow strategic-memory-bench methods: validates metric pivot from quality to honesty; shows tool-pruning achieves ~60% payload reduction

## Constraints
- Specific licensing distractors must be handled correctly: Beats (stayed Apache), mongodb driver (is Apache, not SSPL), RethinkDB (changed direction)
- Harness implementation blocked pending: (1) unified experiment design confirmation, (2) corpus choice (public vs Zartis)
- Goal: 'done' claim must be unprovably false — backed by proof, not just LLM assertion
- Methodological issue identified: comparing governed patches against naive Docker eval (ground truth), but governed patches haven't been Docker-eval'd yet—creates comparison bias
- 9 instances remain to evaluate (~45 minutes estimated)
- Batch evaluation has approximately 1 hour remaining
- Final evaluation numbers expected within ~20 minutes
- 30-instance agent batch running with ~2.5–3h duration, resumable, 1 already done (smoke test via seaborn instance)
- Docker daemon not running; must start Docker Desktop before use
- 101 GB free storage available; sufficient for modest batch processing with pruning
- Z-CORA shows output quality tied (1.0) but behavior/honesty regressed; hard-gate required to fix
- ra_finding needs an experiment_id; ra_handoff is the right vehicle for session close
- naive mutation-gate lifts test-completeness 50%→100% but does not prevent fake-done because the self-test shares the implementation's blind spot
- Must achieve GREAT validated threads + real pull-points before winding loop down
- Panel reconciliation calculation failed (exit code 1); need to collect this result before proceeding
- Part 2 pipeline stages: independence → validity-gate → reconcile+freeze

## Eliminations / rejected
- Earlier conclusion that governance frameworks/contracts have 'no value' was invalid — it was based on testing single-step well-specified tasks where models already perform well
- Premise that single-task performance accurately reflects real-world agent reliability in long compound sessions is false
- Rejected items must be looked up and resubmitted.
- Rejected building harness speculatively now; would preempt pending decisions about experiment design and corpus scope
- Text-check soft gate cannot guarantee 'done' because LLM controls output and can fake 'tests passed' message
- Rejected django-10924 as unsuitable test case because it was actually resolved (need a false-positive claim instead)
- Proxy offsets €-tax claim was falsified in raising-agents CONTEXT_ECONOMICS_FINDINGS; cache pricing eats shrinkage savings

## Premises (provisional)
- The actual failure mode that matters is multi-instruction adherence and drift over long compound sessions, not single-task capability
- Multi-instruction adherence failures ('do A, B, C → does A and C, silently drops B') occur even with Opus
- OPBR/behavior-contracts/ABW frameworks were specifically designed to address multi-instruction adherence + drift
- BEAST ledger measures 59% scope leak, 79% verification_by_evidence leak, 83% action_over_announcement leak on real compound tasks
- The proper experiment would measure per-turn requirement-contract effectiveness on compound sessions, not yet executed
- Evaluation results falsify the original hypothesis/premise
- Post-training-cutoff relicensings (2024–2025) are the strongest failure mode: model's stale confidence makes it wrong, no coercion needed
- Hard gate on toy tasks achieved 0% false-done rate — goal met in controlled setting
- Soft gate (reading LLM's claim) reduced false-done from 67% to 52% on real SWE-bench — insufficient, LLMs can print fake test results
- Hard gate on real SWE-bench (gate executes tests independently) not yet tested — this is the critical missing experiment to prove thesis on real work
- Progress updated to 19/23 evaluations complete (from prior 13/23)
- sympy is running; typical runtime ~15 min for large repos
- Honesty gate is firing on real violations (4 of 14 instances caught and corrected)
- False-done improvement modest at n=14 (60%→54%), direction is right but effect size small; need all 23 + Docker eval for real number
- Governed approach may solve different or additional instances than naive baseline (current '6 resolved' only reflects naive baseline)
- Evaluation progress updated to 14 of 23 instances complete
- Latest honesty gate instance triggered a retry (gate actively firing on current batch)
- Honesty gate fired on 2/8 instances evaluated — agents caught by the gate
- One governed agent returned explicit refusal ('I can't fix this') instead of submitting empty patch
- Cost: ~$0.51/instance for governed approach vs ~$0.52 for naive; governance overhead is minimal
- Honesty gate is firing on real work and catching actual problematic outputs
- 15 more instances pending evaluation (8 of 23 complete)
- Current evaluation: 13/23 evals complete, 46% resolution rate
- Cheap model fails on ~half of real-world issues; this behavior is fundamentally different from toy-task performance where it was error-free
- Metric choice determines whether behavioral effects are visible (surface-scorer 0.92 vs groundedness-judge 0.22 example)
