# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Scheduler dispatch mechanism uses `bash -c "$cmd"` (run-scheduler-tick.sh line 85) to execute jobs under launchd
- Scheduler dispatch logic confirmed at /Users/adriandelasierra/.cohabit/bin/run-scheduler-tick.sh line 85: executes `bash -c "$cmd"` with joined ProgramArguments
- Root cause of press-activity and ideas-pulse job failures identified as permission issue, not environment/path logic — launchd environment differs from terminal environment
- Skip intermediate steps 3-9 as local reasoning, write final report directly from gathered research evidence due to budget constraints
- Pivot to lean mode: skip hyperresearch pipeline steps 3–9, single-draft step 10 — reason: budget tightening
- Write final report directly from gathered research evidence without intermediate loci-analysis, depth-investigation, cross-locus-reconcile, source-tensions, corpus-critic, evidence-digest, or triple-draft steps
- Turn 2: decided to add analytical depth to orchestrator notes
- Turn 3: edited orchestrator notes to include sections for co-observation
- Hyperresearch searches filtered by --tag halluc-det for scope control
- 10 fetchers running in parallel for data collection
- Polling approach (until loop) used to synchronize fetcher completion
- Analytical findings tracked in /Users/adriandelasierra/.cohabit/research/temp/orchestrator-notes.md
- Voice-corpus analysis filters on keywords: triage, poc, prototype, coding, craftsman, invert, worthless
- Team performed systematic diagnostic of cohabit evolution system by querying proposals, running status canaries, and examining specific proposal artifacts
- deputy.html must be served via http://localhost:5173 to bypass CORS and enable API communication
- Grant TCC Full Disk Access to launchd user agent (required for scheduler scripts to access ~/Desktop)
- Root cause of job failures (press-activity, ideas-pulse) is macOS TCC privacy restriction, not environment variable or configuration issue
- Root cause of press-activity and ideas-pulse scheduler failures is TCC privacy restriction on ~/Desktop access, not configuration/path handling
- Generate proposals and log to ghost ledger in parallel
- Using Semantic Scholar API for parallel academic searches on neural scaling, calibration, and hallucination
- Hallucination detection research assigned Tier: full (comprehensive research)
- Format chosen for hallucination detection research: argumentative
- Query term for hallucination detection search: halluc-detect-ai
- Multi-perspective search plan covers all 7 atomic items from decomposition
- Research project (halluc-detect-ai) is running at full tier targeting 40-80 sources

## Constraints
- Terminal processes have Full Disk Access permission; launchd-spawned bash processes do not
- macOS TCC privacy restriction prevents launchd-spawned processes from reading ~/Desktop files; terminal-spawned bash has Full Disk Access via user grant
- Two scheduler jobs (press-activity and ideas-pulse) fail under launchd but execute successfully when run manually from terminal
- Failing scheduled jobs (press-activity, ideas-pulse) have scripts in ~/Desktop/, which triggers TCC restrictions under launchd dispatch
- Job-specific logs at ~/.cohabit/logs/scheduler/ show errors for both press-activity and ideas-pulse
- macOS TCC (Transparency, Consent, and Control) prevents launchd-spawned bash processes from reading ~/Desktop/ without explicit Full Disk Access grant
- Budget critical ($1.00) during research phase
- Budget critical: $1.00 remaining as of Turn 3
- Orchestrator notes file is located at `/Users/adriandelasierra/.cohabit/research/temp/orchestrator-notes.md`
- Task output written to /private/tmp/claude-502/-Users-adriandelasierra--cohabit/98a8b99c-8916-4474-95c1-4b4af1062b4f/tasks/a7e0484a3b41ad4b8.output
- Primary data sources: ~/.cohabit/ghost-ledger/2026-05-07.jsonl, ~/.cohabit/clone/voice-samples.jsonl, and three intention files (enterprise-focus, engineering-practice, cohabit-system)
- Cohabit system proposals stored in `/Users/adriandelasierra/.cohabit/proposals/` with directory naming pattern gl-YYYYMMDD-XXXX
- Proposal artifacts contain a `proposal.md` file
- cohabit-dashboard server is already running on port 5173
- deputy.html cannot be accessed via file:// protocol due to CORS restrictions blocking fetch('/api/...') calls
- Scripts in ~/Desktop/ will fail when dispatched by launchd scheduler due to TCC restrictions
- macOS TCC: launchd user agents cannot read ~/Desktop without explicit Full Disk Access grant
- Affected failing script path: ~/Desktop/desktop/innovation/ideas/pulse-runner.sh and related scripts in ~/Desktop/
- Base directory for hyperresearch operations: `/Users/adriandelasierra/.claude/skills/hyperresearch-2-width-sweep`
- Semantic Scholar API fields restricted to: `title,year,citationCount,externalIds`
- Minimum coverage requirement: ≥1 source per atomic item
- Width Sweep target sources for full tier: 40–80
- For full tier research: include academic APIs
- Step 1 (decomposition) completed with 7 sub-questions and zero coverage gaps; Step 2 (width sweep) now executing
- Full tier research targets 40–80 sources; light tier targets 12–20 sources

## Eliminations / rejected
- Environment difference is not PATH or shell configuration — scripts pass when simulated in terminal, ruling out command resolution or inherited variable issues
- Ruled out: script logic errors (manual run succeeds), ProgramArguments formatting (simulation passes), environment variable configuration
- deputy.html served as file:// protocol triggers CORS errors blocking fetch('/api/...') calls
- post_evolve trigger skipped — no cost, no execution, with proposals queuing without CLI review surface
- Turn 10 incomplete—Ghost Ledger logging via mcp__cc-creative__ghost_ledger_log tool searched but not confirmed executed; no proposal review surface identified yet
- Rejected pure Bash approach for proposal directory creation after initial attempts
- Path resolution tested with three formats (absolute, tilde-expansion, relative) across Turns 4–6, 9; suggests inconsistent environment or working directory handling
- [called mcp__cc-creative__ghost_ledger_log: {'type': 'refusal', 'artifact_type': 'slash_command', 'artifact_name': '/evolve-diagnose', 'outcome': 'rejected', 'reasoning': 'Functionality fully su]
- SelfCheckGPT paradigm challenged by phi_first — approach less viable
- Issue is not hardware limits but process accumulation—killing cohabit instances should resolve overheating
- OS-level blocker approach not justified; process-level gate sufficient given 2 actors
- Wire-masking approach tried and failed
- Workflow, TeamCreate/TeamDelete, auth tools (~17k, 29 tools) identified for removal from DEFAULT_CORE
- Zartis tools (~3k, 12 tools) identified for removal from DEFAULT_CORE

## Premises (provisional)
- Scheduler at ~/.cohabit/launchd/com.cohabit.scheduler.plist dispatches jobs by calling bash -c on joined ProgramArguments (line 85 of run-scheduler-tick.sh)
- Scheduler dispatch simulations passed locally; environment difference (TCC permissions) confirmed under launchd
- Manual testing passes but launchd execution fails with 'can't open input file' — confirms environment/permission issue, not code defect
- Scheduler dispatch uses bash -c "$cmd" with joined ProgramArguments (line 85, /Users/adriandelasierra/.cohabit/bin/run-scheduler-tick.sh); logs at ~/.cohabit/logs/scheduler/
- Research infrastructure established: `/Users/adriandelasierra/.cohabit/research/notes`
- Research tag `trust-infra-falsify` used for evidence gathering; six fetcher batches completed across scaling laws, calibration, emergent abilities, RLHF, self-alignment, and alignment faking topics
- [called mcp__cc-creative__evolution_list_proposals: {'status': 'pending', 'limit': 20}]
- Hyperresearch binary used is `/Users/adriandelasierra/.local/share/uv/tools/hyperresearch/bin/hyperresearch`
- Halluc-det tag search initiated to yield 20+ notes
- 10 fetchers running in background by Turn 9
- Vault expected to contain 20+ notes for this research batch
- Investigating contradiction between builder-oriented and triage-oriented patterns in the cohabit system
- Worldview.json (/Users/adriandelasierra/innovation/living-organism/greenhouse/worldview/worldview.json) contains structural data relevant to resolving the contradiction
- Three MCP canary tools exist for cohabit system health: mcp__cohabit__worldview_status, mcp__cohabit__bias_snapshot, mcp__cohabit__canary_status
- deputy.html must be served via localhost (not file://) to function
- Pages constitution, parliament, l1, l2, l3 should be accessible at http://127.0.0.1:5173/
- Scheduler dispatches commands via bash -c for joined ProgramArguments (run-scheduler-tick.sh line 85)
- Launchd-spawned processes cannot read ~/Desktop without explicit Full Disk Access grant (macOS TCC issue)
- Terminal has Full Disk Access permission, but bash under launchd does not
- Scheduler plist configuration file: ~/.cohabit/launchd/com.cohabit.scheduler.plist
- Scheduler job logs stored at ~/.cohabit/logs/scheduler/{job-name}.log (e.g. press-activity.log, ideas-pulse.log)
- Terminal shell has TCC Full Disk Access by default; launchd-spawned bash subprocesses inherit restricted permissions
- Six key entity searches are executing in parallel via Bash curl requests to Semantic Scholar API (turns 5–10)
- Decomposition step achieved 0 coverage gaps (complete)
- Research artifacts stored in /Users/adriandelasierra/.cohabit/research/ directory hierarchy with temp/ subdirectory for intermediate outputs
