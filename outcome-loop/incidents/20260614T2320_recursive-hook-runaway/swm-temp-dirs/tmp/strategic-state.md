# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Legal gating decision needed: does launch require compliance clearance before shipping or defer to post-ship?
- Governance owner must be identified and assigned accountability
- Measurement framework must be defined with success metrics (engagement rate, proposal quality change, adoption velocity) and collection method
- Steering-committee skill will be made default/recommended in internal Claude agent platform for all product and engineering teams to pressure-test proposals before real stakeholder meetings
- Goal is to give product and engineering teams on-demand simulated stakeholder scrutiny before real meetings; expected benefit is shifting expensive scrutiny left
- Package existing steering-committee SKILL.md as default/recommended skill on internal Claude agent platform
- Target product and engineering teams as users of the simulated committee review capability
- Objective: shift proposal scrutiny left, before real steering meetings occur
- The feature's 'default' behavior must be operationally defined before building: choose opt-in documentation listing versus UI surfacing
- One-page usage guide must be written covering what it is, when to use it, how to interpret output, and explicit non-use cases (not a substitute for real review or org decisions)
- Proposal to package 'steering-committee' skill as default recommended tool in internal Claude agent platform for all product and engineering teams
- Proposal packages existing 'steering-committee' prompt-based skill as default, recommended tool in internal Claude agent platform
- Intended rollout target: all product and engineering teams
- Expected benefit: structured multi-stakeholder scrutiny earlier in process, before expensive real meetings
- Executive recommendation is APPROVE WITH CONDITIONS, not unconditional approval
- A pilot with 2–3 identified teams must precede platform-wide rollout; no pilot plan currently exists
- Approval conditional on resolving three blockers: legal review, data handling policy, and named DRI with eval gate (not unconditional)
- Telemetry explicitly excluded from proposal despite Product wanting measurable outcomes
- Team must choose between inline skill execution or provisioning writ MCP tools
- Approved with conditions: steering-committee skill proved valuable in practice; packaging as platform default is reasonable
- Must establish measurement and validation plan with 6-week eval gate before full rollout
- Pilot with 2–3 early adopters required before platform-wide rollout
- Define scope: which decision types warrant simulated review, which skip it
- Agentic Firewall proposal APPROVED WITH CONDITIONS—not unconditionally approved
- Approval requires four critical gaps to be resolved before engineering: ledger architecture with disaster recovery, evidence validation spec, integration/deployment plan, and customer/user validation

## Constraints
- Must document data-handling policy for proposals containing regulated data (PII, pricing, roadmap)
- Deliverables must be directed at THE PROPOSER with concrete executable steps, not internal Adrian-side governance/infrastructure only
- Legal sign-off required on simulated personas before launch—must document compliance exposure, required disclosure language, and liability framework
- Legal review required before steering-committee skill platform rollout
- Data handling policy must be established before platform rollout
- Named DRI must be assigned for this initiative
- Eval gate must be defined and passed before platform-wide rollout
- Pilot program must precede platform-wide rollout of steering-committee skill
- Proposal must document and resolve dependencies before execution: legal review, data handling policy, named DRI with eval gate
- Proposal documentation must explicitly cover all four elements: objective, scope, key assumptions, and dependencies
- Legal review of simulated persona liability is a blocking requirement before announcement; must submit SKILL.md and sample outputs with a deadline
- Action items must have explicit ownership assigned to specific actors with concrete steps, not passive construction or ambiguous roles—lack of clarity is a failure mode
- Proposal scope restricted to SKILL.md file, docs, two examples, and announcement—no new infrastructure, integrations, or enforcement
- Do not proceed to pilot without sign-off.
- STRUCTURAL SIGNALS (ground truth from tool call log — these dims are computed deterministically; do NOT override):
- Proposal scope is narrow: single SKILL.md file, docs, two examples, and announcement—no platform changes
- Audit logging of invocations required before launch (minimum: timestamp, user, project identifier)
- Legal review is a hard blocker per the Security Officer; no legal review status or timeline currently exists
- A named owner (DRI) post-launch must be assigned; currently none is identified
- Data handling policy must exist before launch defining what is and is not permissible to include in proposals submitted to the skill
- Mandatory output disclaimer must accompany every review; coordination needed with Head of Customer Support
- Risk Rating: High; three major unresolved risks (legal exposure, zero measurement, low adoption masking as coverage)
- One measurable success criterion at 6 weeks post-launch must be defined before implementation
- Legal must review use of simulated executive personas and provide sign-off before launch
- Data handling policy defining permissible proposal content (no customer PII, unreleased IP thresholds) must exist before launch

## Eliminations / rejected
- Current Proposal Summary is incomplete—missing dependencies section; cannot proceed to execution without this
- Proposal summary is missing dependencies: legal review, data handling policy, and named DRI with eval gate are conditional blockers not listed
- Current proposal summary missing explicit key assumptions (teams perceive problem; simulated reviews improve quality) and dependencies (legal review, DRI assignment, data-handling policy, support readiness)
- Telemetry explicitly out of scope in proposal, making Product's measurable-outcomes goal irreconcilable without alternative measurement strategy
- Option to launch without legal review of simulated persona liability was rejected
- Option to proceed without named DRI and ownership model post-launch was rejected
- Rejected: waiting for smarter models to self-solve hallucination problem—classified as dangerous fallacy
- Rejected: relying on LLM to police its own behavior or be honest via prompt engineering alone
- Rejected: platform-wide rollout without pilot validation and early-adopter feedback
- Rejected: shipping without legal review of simulated personas and misrepresentation risk
- Rejected: shipping without comprehensive design and customer validation due to critical risks (ledger corruption, firewall bottleneck, repair loop failures)
- Rejected relying on the LLM to police itself; must place external gatekeepers that force honesty through evidence verification
- Rejected storing epistemic state in LLM context window; replaced with external ledger to prevent hallucination-escape
- Rejected waiting for better models (GPT-5) to solve hallucination—task complexity scales linearly with model intelligence, so narrativization is inevitable regardless

## Premises (provisional)
- Concrete next actions directed at the proposer are required but have not been formulated
- Proposal packages existing prompt-based steering-committee skill as default, recommended tool on internal Claude agent platform
- Hackathon result for steering-committee generalizes to broader team adoption patterns
- Simulated reviews improve proposal quality—this is the central premise and has only been tested in one hackathon session
- Teams perceive a problem with proposal quality or review access; demand is assumed, not validated
- Teams will interpret LLM outputs appropriately and not misrepresent them externally; no guardrails currently in place
- Hackathon evidence of value is single anecdote; broader org demand and adoption willingness unvalidated
- Teams may share simulated review output externally as if it were real stakeholder sign-off—misrepresentation path currently unmitigated
- Platform has capacity headroom for additional workload (not estimated or assessed)
- Teams have sufficient context to write quality proposals (garbage-in risk not addressed)
- Without DRI ownership and measurement, skill will drift in quality, be misused, or become shelfware with no mechanism to detect any of these
- Writ MCP tools (writ_start_run, writ_run_step, writ_end_run) are not currently available in the project toolset
- Steering-committee skill can execute the full review process inline without the writ system
- Writ system would stamp the Attest ledger and compute a trust score
- Narrativization (context-window-driven hallucination under pressure) is structural property of autoregressive architectures under pressure, not solvable by waiting for next-generation models
- Creative probabilistic reasoning in agent process is desirable; deterministic output verification is non-negotiable
- The Agentic Firewall is a permanent foundational architectural requirement for autonomous systems, not a temporary band-aid
- Customers want and will accept verification overhead and potential latency—not yet validated through user research
- Repair loop failures can be diagnosed and operationally responded to—no runbooks specified yet
- Teams perceive a problem with current proposal review and will adopt simulated committee—not yet validated
- Simulated reviews improve proposal quality—no measurement plan established yet
- LLM outputs are consistent and accurate enough for high-stakes decisions—not tested at scale
- Teams will use output appropriately and not misrepresent it—no guardrails in place
- Token cost and platform load at full adoption is acceptable—not estimated yet
- Narrativization is structural consequence of autoregressive architectures under pressure, not a solvable bug in future models
