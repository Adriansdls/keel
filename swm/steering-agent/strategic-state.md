# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Legal review of simulated executive persona liability explicitly deferred to post-launch
- Governance, access control, and enforcement tooling are explicitly out of scope for the initial rollout.
- Platform-wide rollout is planned without a preceding pilot study with defined success criteria.
- Single hackathon usage ('worked well in practice') is sufficient evidence to generalize to platform-wide rollout without additional validation
- Adopt steering-committee skill as default, recommended capability in platform; rationale: worked well at hackathon, shifts scrutiny left before expensive changes
- Make steering-committee skill a default, recommended skill in the internal Claude agent platform for all product and engineering teams
- Announce the skill to product and engineering teams
- Provide documentation and two invocation examples with the rollout
- Legal and compliance review of simulated executive personas deferred to post-launch; launch gate does not include legal clearance
- Skill available to all product and engineering teams with no documented access controls, approval gates, or usage restrictions
- Adoption plan limited to 'announcement to teams'; no owner assignment, engagement cadence, or rollout schedule defined
- Adopt steering-committee skill as DEFAULT and RECOMMENDED in internal agent platform, scoped to product and engineering teams
- Package existing steering-committee SKILL.md as default skill in platform
- Include documentation with two invocation examples
- Steering-committee skill will be packaged as default, recommended skill in internal Claude agent platform
- Adoption package includes documentation, two invocation examples, and announcement to product and engineering teams
- Adoption plan is missing: 'announcement to teams' is a tactic, not a plan. No owner assigned, no adoption targets, no engagement strategy, no measurement of actual usage or sustained adoption post-launch.
- Recommend conditional gate approval requiring legal sign-off on simulated persona liability, data handling policy, access control, and secrets detection before launch
- Chosen prose-only delivery (SKILL.md documentation) without infrastructure, audit logging, or access control mechanisms
- Deferred success metrics and telemetry to post-launch rather than establishing baseline measurements pre-launch
- Planned announcement-based rollout without detailed adoption plan, owner assignment, or engagement targets
- Scope includes packaging existing SKILL.md as default, creating documentation with two invocation examples, and announcement to product and engineering teams
- Packaging the existing steering-committee SKILL.md as a default skill in the platform, with documentation and two invocation examples
- Announcing the skill to product and engineering teams is part of the rollout plan
- The skill will be made available to all product and engineering teams

## Constraints
- Business-sensitive inputs (roadmap, pricing, architecture, customer details) will flow to Claude platform with no data classification policy or automated secrets detection.
- No audit logging or tracking mechanism exists to record proposal inputs, output access, or downstream decision use.
- Adoption plan contains no named owner, engagement cadence, or adoption targets beyond announcement.
- No audit logging, telemetry, or tracking mechanism exists to record proposals input, outputs accessed, or downstream decisions
- No budget for new infrastructure; solution must run on existing Claude platform seats
- The steering-committee skill is prose-only: a single SKILL.md file, no code, no external dependencies
- Legal has not reviewed the use of simulated executive personas in written outputs
- Legal has not reviewed compliance or liability implications of simulated executive personas in written outputs; critical blocker
- Simulated personas in written outputs have not been reviewed by legal, compliance, or security teams for liability or data-handling implications
- No audit trail or telemetry exists to track what proposals were reviewed, which personas reviewed them, or resulting decisions
- No baseline measurement framework exists pre-launch to validate core claim that simulated scrutiny improves proposal quality
- No data classification policy defined for what confidential content (roadmaps, customer data, financials, competitive strategy) teams may submit
- No data retention, redaction, or deletion controls documented for confidential content in simulated reviews
- No secrets management policy exists for detecting, redacting, or preventing credentials in proposal text before platform submission.
- No access control or authorization policy restricts which users can invoke the skill or on which proposal types (confidential vs. non-sensitive)
- No audit logging, retention policy, or forensic trail mechanism exists to track skill invocations, inputs, outputs, and who triggered reviews.
- Legal review of compliance and liability implications of simulated executive personas in written outputs is required before rollout but has not been completed.
- No data classification, handling policy, or residency controls defined for confidential proposal content submitted to Anthropic platform.
- Measurement framework and baseline metrics to validate whether simulated reviews improve proposal quality or correlate with downstream outcomes must be defined before launch.
- Rollback plan required if legal review surfaces unmitigable compliance risk or post-launch measurement shows no value correlation.
- No telemetry exists to measure whether simulated reviews improve proposal quality or correlate with downstream outcomes
- No access control policy specifies who can invoke the skill, on which proposal types, or under what conditions
- Evidence of value limited to one hackathon usage where product team found it 'worked well in practice'; no systematic measurement
- No data handling policy exists for confidential proposal content (proprietary algorithms, financial data, customer lists, credentials)
- No audit trail mechanism exists to document who triggered reviews, which proposals were submitted, when, or retention duration

## Eliminations / rejected
- Dropped: integration with ticketing systems, automated triggering on PRs, custom personas per team, enforcement/governance tooling from initial scope
- Out of scope: integration with ticketing systems, automated PR triggering, custom per-team personas (future iteration), enforcement/governance tooling
- Automated triggering on PRs is out of scope
- Enforcement or governance tooling is out of scope
- Out of scope: custom personas per team (deferred to future iteration)
- Custom per-team personas are deferred to future iteration; not in this proposal
- Ticketing system integration out of scope
- Ticketing system integration excluded from this proposal
- Automated PR triggering excluded from this proposal
- Enforcement or governance tooling excluded from this proposal
- Code-based infrastructure approach eliminated; prose-only solution chosen to minimize build cost
- Phased rollout with systematic measurement eliminated in favor of immediate platform-wide announcement
- Integration with ticketing systems is out of scope
- Finance director dropped from committee—no budget impact; runs on existing seats
- Head of customer support dropped from committee—scope is internal tooling; no customer-facing change
- Head of sales dropped from committee—no revenue, pricing, or customer relationship impact
- Operations/DevOps lead dropped from committee—prose-only skill, no infra, no deployment pipeline affected

## Premises (provisional)
- Teams will treat simulated reviews as advisory and not quote them as authoritative stakeholder feedback, but no mechanism enforces this distinction
- Generic default personas remain effective across 10+ teams without per-team customization or quality degradation
- Adoption will sustain beyond novelty fade despite absence of assigned owner, engagement cadence, or explicit adoption targets
- Prose-only delivery is sufficient for initial launch
- Legal review of simulated personas can be deferred to post-launch
- One hackathon use case (Metacompliance product team found it 'worked well in practice') is sufficient evidence for platform-scale rollout
- Prose-only delivery (SKILL.md with example prompts) is sufficient; no infrastructure, guardrails, or access control mechanisms needed
- Teams will not misattribute simulated reviews as actual executive input in downstream use (Slack, PRDs, compliance records)
- Legal liability for simulated personas is manageable as a post-launch concern; deferring review is acceptable risk
- Hackathon success (one instance where product team found it 'worked well in practice') transfers to platform default use case
- Simulated personas generating executive-like feedback create reputational and liability risk if output is attached to or conflated with real stakeholder decision-making without clear audit evidence of simulation and non-binding status.
- One product team's 'worked well in practice' at a hackathon (no metrics) does not establish platform-wide readiness or justify single default committee composition for diverse product and engineering domains.
- Early scrutiny via always-available simulated committee reduces cost and latency of proposal rework (core value hypothesis, unvalidated)
- Teams can reliably distinguish simulated stakeholder feedback from real governance consensus in practice
- Existing Claude platform seats have spare capacity to absorb new skill volume without cost or latency impact
- One hackathon usage where simulated reviews 'worked well in practice' generalizes to platform-wide readiness
- All teams will understand simulated executive personas as non-binding feedback without risk of conflation with real stakeholder consensus
- Legal review of simulated personas will not surface unmitigable compliance risk or become a launch blocker
- Single default committee composition serves diverse product and engineering domains without domain-specific customization
- No adoption friction; teams will sustain usage from announcement alone without engagement strategy
- Proposals reviewed may contain proprietary algorithms, financial data, customer lists, or credentials
- Project at /Users/adriandelasierra/steering-agent is unindexed and not currently tracked in ra-pm
- Simulated personas could mislead users into treating simulated opinions as vetted stakeholder input, creating reputational and liability risk
- Evidence of value is limited to one hackathon usage where product team found it 'worked well in practice'; no systematic measurement or instrumentation
- No telemetry exists yet to measure correlation between simulated reviews and downstream proposal acceptance or governance quality
