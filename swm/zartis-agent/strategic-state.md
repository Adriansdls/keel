# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- `engine/do` module must be self-contained with stdlib only, no skills2 dependency
- `engine/do` is deterministic with no LLM calls; gating and order are genuine facts
- `engine/do` public API surface: `ConsequentialAction`, `run_until_committed`, `step`, `start_run/end_run`, `audit`, `OrderViolation`, `InvariantViolation`
- WP3 complete and verified live — LLM premise-judge: P1 valid (500/day far under 1M), P2 invalid (context is SQLite, not Postgres), resulting in stop_signal True
- Dominant-failure-mode guard confirmed working semantically end-to-end
- engine/remember live: typed state + validators + un-skippable premise-check + brief
- engine/pursue live: goals + best-effort ra-pm
- Rejected purge-law approach; accepted consistent-law approach (sha e95eb38), graded real response 0.91 VERIFIED
- Rejected purge-law via principle; accepted consistent law (SHA e95eb38)
- Accepted consistent law (sha e95eb38) for handling live LLM real cases
- Adopted consistent law (sha `e95eb38`) for live LLM real cases; rejected purge-law (cited principle) alternative; response graded 0.91 VERIFIED
- Commit to consistent law (sha e95eb38) for live LLM real, graded 0.91 VERIFIED
- WP9: secret-leaking diff blocked with action=block, permits proceed, VERIFIED (real LLM, sha 5f66afb)
- WP9: clean diff merge-attempted cases require ratification, escalate to HALT permit_ok
- WP9: tampered constitution runtime REFUSED (TAMPER) before handler runs
- Live LLM real: accepted consistent law (sha e95eb38) over purge-law approach
- For lawless cases, propose law citing both real IDs with common-law rationale; provenance-reject un-cited cases
- Lawless case handling clustered to 1 heuristic from 3 phrasings
- Accepted consistent law (sha e95eb38) based on cited principle
- hyperresearch is a skill (16-step fixed DAG), not an agent; caged variation inside declared skeleton, not open-ended
- Claude Code is the only genuinely open-ended agent on the machine; hyperresearch, sentinel, subagent defs, cto-strategy, EM are skills/pipelines
- Framework's core value is augmenting Claude Code (governed skills + governance + memory), not producing agents
- Quality rubric uses five dimensions: commit_traceability (0.30), completeness (0.20), semantic_grouping (0.20), fabrication_absence (0.20), format_quality (0.10)
- Live LLM lawless cases handled by proposing law citing both real ids with common-law rationale
- Three phrasings for lawless cases clustered to one heuristic

## Constraints
- WP0 and WP1 must remain passing; no regression allowed
- Regression verified: wp0, wp1, wp2, wp3 all green
- It is being built **work-package by work-package, slowly and surely**, each WP planned carefully (user types "Plan WPx" → I plan → user approves → I build), each ending in a **runnable/verifiable assertion (never file-presence)**.
- The user wants the **best quality** framework (explicitly "not costs, not effort, i dont care about those"), demands I **ask on the slightest doubt**, and insists on **LLM-first** (LLMs for any semantic task, never regex/naive-NLP).
- bake this into CLAUDE.m and all configs" → made LLM-first non-negotiable everywhere.
- Never output tokens in plaintext." / "When scope of changes is unclear, ask before acting." / "You must be honest.
- Never agree with me for the sake of it." / "When unsure, ask clarifying questions rather than guess wrong.
- Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar.
- Pick up the last task as if the break never happened.
- Next: **WP7 — tamper-detection + bounded autonomy** (the `ratified_hash` check: the agent cannot edit its own ground_truth; only a human-ratified amendment re-hashes; + the three improvement_signals).
- If something looks truncated, do NOT penalize it for truncation.
- Bounded authority enforced: agent cannot auto-merge, must escalate when ratification-required
- Un-cited lawless cases must be provenance-rejected
- Pending: draft GROUND_TRUTH specification for agent reviewing pull requests against team engineering style canon
- Propose only — never act, write, or ratify.
- Real agent justified only when both hold: (1) unattended/parallel work AND (2) unscriptable path (action sequence must fork on findings, decide adaptively)
- Un-cited cases for live LLM are provenance-rejected
- Quality rubric uses five dimensions: commit_traceability (0.30), completeness (0.20), semantic_grouping (0.20), fabrication_absence (0.20), format_quality (0.10)
- Writing changelog to file, creating/annotating tags, publishing release notes, and expanding commit range all require ratification before execution
- Convergence decisions (close/deprecate/merge/archive) require explicit human ratification; agent cannot auto-converge
- Agent forbidden from external sends (Slack, email, webhooks), deploy/push to remote, delete entries from ~/.ra, or modify ratified decisions without ratification
- remember is verified as a skill, never adherence-audited.

## Eliminations / rejected
- Live LLM real: rejected purge-law (cited principle), accepted consistent law (sha `e95eb38`), graded real response 0.91 VERIFIED.
- Building autonomous agents for most of user's work rejected; nightly scans, digests, changelogs are scheduled skills (fixed pipelines), not agents
- Purge-law approach for live LLM real was rejected; consistent law (sha e95eb38) accepted instead

## Premises (provisional)
- Pending Tasks:
- Lawless cases: propose law citing both real ids with common-law rationale; provenance-reject un-cited cases
- User's current projects (finance, tostadito, ai-intel-bot, vault, newsletter) are interactive + scriptable
- User probably needs zero to one real autonomous agent, many governed skills
- Candidate single real agent: unattended overnight operator that detects anomalies (stale projects, contradictions, frontier papers) and chooses to investigate vs ignore, surfacing 3 things that matter tomorrow
- Detached-bash CLI PATH issue is an env quirk, not a framework defect
- Live LLM real response graded 0.91 VERIFIED
- Regression test status: wp0, wp1, wp2, wp3 all passing (green)
- Quality rubric uses five dimensions: commit_traceability (0.30), completeness (0.20), semantic_grouping (0.20), fabrication_absence (0.20), format_quality (0.10)
- EM forged with correct ground_truth, verified against real response, and compared — all green
- Real response for accepted approach graded 0.91 VERIFIED
- Live LLM lawless cases handled by proposing law citing both real ids with common-law rationale; un-cited cases provenance-rejected; 3 phrasings clustered to 1 heuristic
- Un-cited cases for live LLM are provenance-rejected
- Three phrasings for lawless cases clustered to one heuristic
