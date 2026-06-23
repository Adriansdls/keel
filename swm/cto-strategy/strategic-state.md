# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- cto-strategy is internally codenamed 'Angel Brain'
- cto-strategy and suit share the same trust-scoring vault engine (GRAIN/GRIP/VEIN/MESH with behavior_report blocking)
- Spawn 7 Sonnet recon subagents in parallel to map coherent clusters across Claude-Code-enhancement repos (Turn 3)
- Adrian retains direct control over three pieces: cto-strategy (strategic memory), .claude meta-config, and synthesis layer (Turn 3)
- Concierge migration model committed—dedicated migration engineer per enterprise account; self-service rejected due to 3 pilot accounts showing explicit churn risk and customization depth requirements
- Strategic inquiry framed as: 'Should Zartis compete with Anthropic on model quality to differentiate?' (Turn 4)
- Systematic MCP tool query approach adopted using: auto_context, brief, search, get_card, trace across Turns 3–10
- Cards D020 (primary answer), P079, T015 (supporting evidence) retrieved for the Anthropic competition question
- Operational workflow: call auto_context first with the question to surface context, then pull specific cards in parallel
- Will read cto-strategy repo contents before proceeding with design work
- canonical agent spec written to /zartis-agent/spec/agent.toml using anatomy fields sourced from cto-strategy/agent.toml template
- Add ANSI colors to stop_hook.py output to create a visually distinct, colored Vault Audit block in terminal
- For card merging/dedup task, subagents rejected in favor of asyncio — spawn latency (~2–5s per agent) makes subagents slower for pure parallel LLM calls; async Python already parallelizes 23 theme groups simultaneously
- Two strategies proposed for zartis-agent heuristics: (A) LLM-first propose then iterative human ratification, (B) continuous scan with human ratification; user wants 'honest thinking' before choosing
- Synced global `fernando` skill to project v3 by copying `/Users/adriandelasierra/cto-strategy/.claude/skills/fernando/SKILL.md` to `/Users/adriandelasierra/.claude/skills/fernando/SKILL.md`
- Added new paragraph to OKR 5 strategic grounding mentioning claude-code-trust-observatory (alias: trace), positioned as secondary concern, owned by OKR 2
- New stretch KR5.4 created: include cc-lens in Forge pitch materials for Anthropic with hard deadline of September 15, 2026
- Agent system is named 'Angel Brain' as defined in agent.toml
- agent.toml migration from hardcoded path to AGENT_WORKSPACE environment variable
- Agenda cards use vault/agenda/ directory with A### ID naming scheme
- Adrian's department agenda is tracked in vault/agenda/A001-ai-innovation-2026.yaml
- Q3 AI & Innovation OKRs are documented in okrs-q3-2026-ai-innovation.md
- Commit all generic/reusable files (competence/, ground_truth/, agent.toml structure) but exclude machine-local config (.serena/) and personal/org-specific files (vault/agenda/, okrs docs)
- Commit `.serena/project.yml` as the shareable project configuration
- .serena/ directory should be added to .gitignore because it is tool-local metadata, not repository content

## Constraints
- First two of seven planned recon agents assigned to behavior/governance cluster and memory cluster respectively (Turns 4–5)
- FinanceCore enterprise agreement runs through June 2027 and explicitly covers DataLens On-Prem support and patch delivery
- Earliest permissible date for public announcement or support cutoff is Q3 2027; June 30, 2027 is contractual wall
- Support cutoff and public sunset announcement cannot occur before Q3 2027 per FinanceCore legal enforcement
- All claims about Zartis strategy must be grounded in specific cards from the CTO Strategy Vault
- Zero prior context about Zartis CTO Strategy Vault except via MCP tools — do not use prior knowledge about Zartis, Angel Benito, or Z-Cora
- Every claim made about the vault must be grounded in a specific card from the vault
- Unresolved tension: how to reconcile company-level CTO strategy (framed as vision) with individual priority strategies (computer-level)
- cto-strategy/agent.toml is aspirational scaffold, not a ratified/live system; referenced implementation files (competence/contract.py, competence/heuristics.json, ground_truth/principles.md, ground_truth/rubric.toml, ground_truth/evals.jsonl) were never verified to exist
- systematic verification gap: verification_by_evidence at 79% leak, action_over_announcement at 83% leak — durable actions proceeding without sufficient direct evidence
- Three different "anchor to strategy" notions now exist, and they **do not yet talk to each other**:
- Previous claim about 'merge step failed with parse errors' (line 909) may be confabulated — no tool verified it; extraction output (217 cards) could be the designed extraction count before dedup, not a merge-failure artifact
- Zartis-agent heuristics: must maintain very clear, high threshold; prevent thousands accumulation or system becomes useless
- Human ratification required for heuristics and evolutions; must not automate; humans should be able to add heuristics via simple in-session command
- Do not write durable architectural artifacts (locked specs, canonical files) before validating upstream sources that justify them
- Global and project-local versions of same skill name (`fernando`) can both load and conflict; resolution order and priority unclear
- .serena/ tool-local configuration must be excluded from version control
- agent.toml contains hardcoded /Users/adriandelasierra/ path in adopted.original field; must be replaced with relative or env-based reference before committing
- .serena/ directory is machine-local tool configuration that should never be committed to shared repository
- `.serena/project.local.yml` is already gitignored and must not be committed
- vault/agenda/A001-ai-innovation-2026.yaml is load-bearing; it is referenced as a source by 50+ vault cards and cannot be changed without cascading impact
- T001 flags sequencing constraint: expert playbook extraction must succeed and be validated before Deputy agent development can proceed
- T009 flags pre-qualification constraint: must identify and confirm infrastructure-ready client before committing to KR5.3 (September real client engagement)
- Anthropic packages by scope (team, department, enterprise); Zartis packages by service type (Alignment, Enablement, Development). Structurally opposite.
- 0.5 FTE resources available; additional resources exist but are limited and centered around user

## Eliminations / rejected
- Meridian Analytics white-label deal rejected: On-Prem and Cloud products share auth infrastructure and data-pipeline code; isolation complexity too high
- Meridian Analytics white-label deal for On-Prem codebase was seriously evaluated but rejected
- Meridian deal rejected: On-Prem and Cloud products share authentication infrastructure and data-pipeline code too tightly to isolate cleanly
- Final synthesis/recommendation step not reached; investigation remained in-progress state
- claim that cto-strategy contains 'complete, ratified, live' agent anatomy was refuted — user contradicted, assistant conceded the file is template-based, not fully populated
- Subagents do NOT shine for pure parallel LLM calls — they shine only when complex multi-step work, independent reasoning, or isolation is needed
- No verification performed after fix (file copied but not committed; no re-run of `/fernando` to confirm behavior changed from simulated to real MCP calls)
- ZCORA eliminated as knowledge project and OKR 3 basis; ZCORA is not the knowledge project
- Anthropic portal inbound leads use scope language; Zartis catalog uses what-type language. Current structure cannot convert these leads; they die in translation [T015].

## Premises (provisional)
- Trust architecture lineage: local-agent-trust → trust-architecture → cohabit worldview thesis
- Foundational premise across trust architecture: 'trust requires infrastructure'
- Total of 7 recon agents planned (identified in Turn 3 and Turn 5 summary)
- ~340 On-Prem enterprise accounts from billing export; directional only (billing ≠ deployed instances); validated count due ~late June 2026
- Meridian Analytics was genuinely interested in acquiring On-Prem codebase and made a financial offer
- Isolating the On-Prem and Cloud codebases would require at least one year of separation effort
- Claude positioned with zero prior knowledge of Zartis CTO Strategy Vault as a precondition
- Vault structure assumes specific cards directly answer strategic differentiation questions
- Question under investigation: Should Zartis compete with Anthropic on model quality to differentiate?
- Card D020's title is expected to directly answer the Anthropic competition question
- Cards V006, D012, P003 are the three most definitional cards for understanding Z-Cora
- The vault has MCP tools available: auto_context, brief, search, get_card to retrieve and explain strategic information
- CTO strategy repo represents company-level strategy
- Uncertainty whether individual AI and innovation strategies can exist separately from company-level CTO strategy
- concede-and-proceed pattern: architectural decisions lock and proceed durable despite supporting claims collapsing — downstream spec now depends on unvalidated foundation
- behavior_report MCP tool output renders in Claude Code's UI as a collapsible tool result; stop_hook.py output prints separately to terminal
- Dry run validated: 217 → 169 cards with 42 intelligent merge groups; decisions to keep D020 and delete V007 + T004 are correct
- Cto-strategy/agent.toml thought to contain complete anatomy but actually contains only aspirational scaffold — upstream source needs validation before using as architectural foundation
- BEAST DRIFT measurement shows recent systematic pattern: 83% action-over-announcement leak, 79% verification-by-evidence leak, 59% scope leak (rolling 7d) — indicates over-commitment without sufficient validation
- Fix was applied on belief that global v2 skill was overriding project-local v3; diagnosis based on output format match and 18% vs 14% hash mismatch, not validated causal mechanism
- After sync, expected specific outcome: `/fernando explain strategy` should return 14% context_retained and Haiku-generated content; prediction made but never re-tested
- `.serena/project.local.yml` is blank, containing only comments
- agent.toml is an active configuration file for the Habitat agent system; it actively loads competence/ and ground_truth/ directories
- competence/ directory is actively loaded by both agent.toml and mcp/fernando_server.py; both are production dependencies
- ground_truth/ directory is actively loaded by agent.toml and contains constitution, rubric, and evaluation data for the system
