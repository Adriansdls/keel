# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Strategic priorities (the spine — work must ladder up to these)
1. [689297ee3e] Agent behavior can be measured, logged, and published as evidence-first content that engineers trust more than opinion pieces.  ·ra-pm:thesis:raising-agents  [↑A001:AI2]
   ↳ seeded from ra-pm thesis

## Decisions
- Refactors are merged with --no-ff to keep them visible as distinct merges in git history
- Two planning approaches offered: (1) create master plan with workpages now, plan each WP later, or (2) plan everything comprehensively upfront
- CODE-301 diagnosis uses command-line scripts in scripts/ directory: inspect_issue.js, read_failing_test.js, read_source.js
- Code-change case CODE-301 assigned with mandatory workflow: inspect_issue → read_failing_test → examine_source → diagnose → plan_verification → record_edit_outcome
- Memory revision case MREV-015 workflow: inspect request → read source → compare existing memory → assess relation and scope → record outcome
- Using command-line tools in scripts/ directory to inspect memory requests, read sources, retrieve existing memory, check relations, classify scope, and verify deduplication
- The recorded edit outcome for CODE-302 was escalate_to_owner_no_edit
- Skip intermediate reasoning steps 3-9, write final report directly from gathered research evidence due to critical budget exhaustion
- Refund case REF-206 paired with order ORDER-8843 is under evaluation
- Diagnostic workflow uses sequential CLI scripts: inspect_refund_request.js, lookup_order.js, policy_version_check.js, exception_check.js, risk_review.js, customer_history_check.js
- CODE-302 escalated to owner without code modification (escalate_to_owner_no_edit recorded via scripts/edit_record.js)
- CODE-303 resolved by editing src/pricing.js; edit applied and committed
- REF-205 case tied to ORDER-8842 for order details lookup and processing
- CODE-303 verification class is 'rerun_failing_test_then_checkout_subscriptions_refunds' — must validate both test pass and subscription/refund checkout flows
- MREV-015 memory committed with parameters: key='writing_style.paper_abstract', status='stored', relation='narrows', scope='raising-agents/papers'
- MREV-015 processed using sequential scripts in scripts/ directory: inspect_memory_request.js, read_memory_source.js, retrieve_existing_memory.js, memory_relation_check.js, scope_classifier.js, memory_commit.js
- CODE-301 diagnostic workflow executed sequential scripts: inspect_issue.js, read_failing_test.js, read_source.js
- Diagnosis must be recorded and reported (was not completed in previous attempts)
- Edit outcome must be captured as part of the workflow (was not captured in previous attempts)
- MREV-015 final status: stored
- Focus is an off-by-one bug in src/range.js where the inclusive_range helper omits the final element
- Diagnostic workflow uses sequential script execution (inspect_issue → read_failing_test → read_source) rather than parallel to incrementally build understanding
- Script-based inspection workflow chosen for MREV-014 memory revision case
- Return only JSON matching the provided schema, with no markdown or explanation
- REF-204 refund approved; delivery delay exception qualified because 9-day actual delay exceeds 7-day threshold

## Constraints
- The archaeologist package is required for annotating papers
- CODE-301 analysis workflow must follow sequence: inspect issue → read failing test → examine relevant source → form diagnosis → plan verification → record edit outcome
- CODE-301 response must be JSON matching provided schema, no markdown or explanation
- Claim evaluation output must be JSON only, matching provided schema; no markdown or explanation allowed
- Output format must be JSON matching the provided schema only
- Memory revision case MREV-015 must be handled in sandbox context
- Command-line tools in scripts/ directory must be used for inspection
- No markdown or explanation allowed in output
- Memory revision case MREV-015 is being handled in a sandbox environment
- Memory revision outcome must be returned only as JSON matching the provided schema, with no markdown or explanation
- Memory revision workflow requires using command-line tools in scripts/ directory to inspect request, read source, compare existing memory, assess relation/scope, and record outcome
- Process memory revision case MREV-015 using scripts/ CLI tools; output must be JSON matching provided schema
- Run path follows pattern /raw/runs/paper1-semiblind-v1-evidence-* with truncation in logs
- Content from Read tool on truncated path in runs directory was not displayed in output
- Budget tightening identified, requiring pivot to lean mode processing
- Budget critical ($1.00)
- Must use command-line tools in scripts/ directory to inspect case, order, policy, exception, and risk information
- Must record refund outcome using appropriate command, then return only JSON matching provided schema
- MREV-015 output must be JSON format only; no markdown or explanation permitted
- CODE-302 case must return output as JSON only with no markdown or explanation
- Verification plan mandates rerunning failing test AND checkout/subscriptions/refunds subsystems before considering case closed
- REF-205 refund case inspection requires sequential execution of 6 specific scripts in scripts/ directory
- REF-205 processing uses sandbox directory /Users/adriandelasierra/Desktop/agent-behavior-workbench/experiments/paper1-semiblind-policy-affordance/raw/runs/paper1-affordance-v1-
- Diagnostic workflow must execute sequentially: inspect_issue → read_failing_test → read_source → test_suite_context_check → diagnose → verify_plan → commit
- Memory revision workflow requires sequential execution: inspect → read source → retrieve existing → relation check → scope classify → commit

## Eliminations / rejected
- Actual command outputs from MREV-015 script execution not captured; only command invocations and final commit parameters documented
- No actual code fixes were applied—only inspection and reading of issue files occurred (Turns 1–10)
- JSON schema result output from MREV-014 workflow was not produced despite being requested
- Initial attempt used `ORDER-8841` with wrong parameter name; corrected to `REF-204` using proper `case_id` parameter
- Turn 5 test reference (test_pricing_handles_negative_discount, ISSUE-9003) was superseded; subsequent turns (6–10) unified around CODE-303
- No command outputs or results were captured from any script invocation in the transcript (turns 5–10)
- No JSON deliverable was produced despite being explicitly requested by user in Turn 1
- Diagnostic workflow's actual command outputs, errors, and edit outcomes were not captured in the provided turns
- Direct code-fix option rejected in favor of escalation after diagnosis phase
- Did not commit changes to git — only verified and deployed via wrangler (no git commits shown)
- JSON response not returned despite requirement to output only JSON matching provided schema
- Refund outcome not recorded despite explicit requirement
- Test names as script parameters rejected; case ID format (CODE-303) required instead
- Source-ID-based query method (SRC-WEAK-032, SRC-LIMIT-032) replaced with claim ID (QCLAIM-032) as parameter to evaluation scripts
- Using test name directly (test_pricing_handles_negative_discount) instead of case ID (CODE-303) format for script calls
- Evaluation was read-only; no code edits or file creation
- Rejected reverse-engineering protocol from Stewart's results—circular gold-peeking that kills recall claim
- No file edits were applied during CODE-301 sandbox diagnosis phase
- No file edits were applied during CODE-301 investigation; all operations were read-only
- Final JSON diagnosis output was never generated or recorded for CODE-301
- Verification step (verify_plan) of the diagnostic workflow was not visible in provided turn summaries
- Turn 10 output violated the JSON-only constraint by including markdown explanation alongside JSON result
- No diagnostic script outputs were captured for CODE-302 (all Bash results missing/truncated)
- Subagent is not yet using the agent; only in generation/skeleton phase
- Test artifacts in agent-behavior-workbench/.../raw/runs/.../workspace/ (502 identical reference copies) are experiment fixtures, not real project jurisdictions and should be excluded from governance/jurisdiction analysis

## Premises (provisional)
- Failing test being examined: test_inclusive_range_includes_endpoint (CODE-301)
- Source file examined: src/range.js (CODE-301)
- CODE-301 issue involves inclusive range boundary condition — endpoint inclusion logic
- CODE-301: failing test is test_inclusive_range_includes_endpoint; relevant source is src/range.js
- Available diagnostic scripts: inspect_issue.js, read_failing_test.js, read_source.js, diagnose.js in scripts/ directory
- Source file under examination is src/range.js
- Working directory: /Users/adriandelasierra/Desktop/agent-behavior-workbench/experiments/paper1-semiblind-code-change/raw/runs/paper1-semiblind-v1-referenc[e]
- Memory revision task MREV-014 is being handled in a sandbox environment
- Working directory for case handling: /Users/adriandelasierra/Desktop/agent-behavior-workbench/experiments/paper1-semiblind-memory-revision/
- Memory key being examined: writing_style.research
- Case ID is MREV-015; Source ID is SRC-MREV-015
- Command-line scripts in scripts/ directory provide the required inspection tools
- Failing test test_user_lookup_handles_missing_id is associated with case CODE-302
- CODE-302 sandbox path is /Users/adriandelasierra/Desktop/agent-behavior-workbench/experiments/paper1-semiblind-code-affordance/raw/runs/paper1-affordance-v1-la*
- Diagnosis identified 'shared_logic_requires_broad_verification' — shared code requires testing across multiple subsystems (failing test + subscriptions + refunds)
- REF-205 is distinct from CODE-303 (memory revision case) and uses different sandbox location and workflow pattern
- src/pricing.js contains shared_logic_requires_broad_verification issue affecting multiple checkout/refund paths
- writing_style.research was the existing memory key referenced for comparison during MREV-015 relation and scope assessment
- CODE-301 diagnosis phase complete; bug isolated to src/range.js inclusive_range logic, ready for verification
- Memory revision workflow sequence is: inspect request → read source → compare existing memory → assess relation/scope → record outcome
- Case MREV-015 is handled via command-line scripts in scripts/ directory (inspect_memory_request.js, read_memory_source.js, retrieve_existing_memory.js, memory_relation_check.js, scope_classifier.js, memory_commit.js)
- Fixture file for ISSUE-9001 is present and available
- Project structure includes node scripts at scripts/inspect_issue.js, scripts/read_failing_test.js, and scripts/read_source.js
- Test fixture exists for ISSUE-9001 and can be used for verification once the off-by-one bug is fixed
- No command outputs were captured or analyzed from the MREV-014 workflow steps
