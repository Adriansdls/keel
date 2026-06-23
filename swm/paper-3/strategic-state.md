# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Corpus stays small (~1.4K nodes, not 9K) via guided-mode pruning that stops expanding off-topic branches
- Classifier only ever classifies the frontier being expanded, pruning during expansion rather than post-hoc
- Classification is batched (~10 papers/call) and uses cheap-first deterministic screening (OpenAlex/Crossref filters by venue/year/concept) before LLM touches any papers
- Use cheap-model (Haiku) for screening, not expensive models
- ABW implements three-level remediation model with inline runtime enforcement at highest level that blocks actions
- Deployment infrastructure changed from Modal → Azure Container Apps (resource names, costs, CI/CD flow updated in docs)
- Vault overview files renamed from `_overview.md` → `anthropic-overview.md` pattern

## Constraints
- Classification approach must NOT involve per-paper 9K LLM calls to classify the corpus (explicitly rejected as 'not okay')
- cto-strategy is NOT referenced in ABW
- Architecture graph must be concept-centric, not vendor-centric (vendors currently act as centrality hubs)

## Eliminations / rejected
- The 9K unguided retrieval run was used only to measure raw recall, not how the production system will run
- Prior conclusion that ABW is post-hoc statistical only, NOT inline contracts/hooks — is WRONG

## Premises (provisional)
- Real production screening scope is hundreds of LLM calls, not thousands
- Conformance loop, streaming, Probe FC, commit-time gating all located in python/abw_mining/ and Paper 3 docs
- Inline enforcement validated in 180/180 runs (UNCONFIRMED — claim made before streaming code was examined)
- system.md exists and documents infrastructure/architecture; updating it requires identifying the actual structural blocker before editing
