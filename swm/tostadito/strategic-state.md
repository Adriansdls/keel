# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Claude Haiku called exactly once for OCR via vision in telegram/route.ts
- Architecture uses Vercel Cron push pattern, not persistent processes
- Determinism first principle: all intelligence in Tostadito is SQL + arithmetic, not LLM-based (Claude Haiku called only once for OCR)
- Agents use Vercel Cron for push, not persistent processes
- Fix all three affected insertion points as one batch (gocardless/sync/route.ts, enablebanking/sync/route.ts, scripts/import_cgd.mjs) rather than separately

## Constraints
- Tostadito uses determinism-first architecture: SQL + arithmetic only, no LLM-based analysis
- All analysis, alerts, and projections must be deterministic with no LLM hallucination
- Claude Haiku invoked exactly once in the entire system: OCR of tickets via vision in telegram/route.ts
- Analysis, alerts, and projections must be entirely deterministic; the model must never hallucinate an expense
- INSERT OR IGNORE deduplicates by ID only, not by content, causing duplicate records when ID matches but content differs

## Premises (provisional)
- Agents in Tostadito employ contracts or SUIT pattern to guide behavior (user inquiring about agent patterns with MCPs in Turn 9)
- Project name is 'Tostadito' with finance MCP server and workflow contracts module
- The deduplication issue affects multiple sync routes, not limited to import_cgd
