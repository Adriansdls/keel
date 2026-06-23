# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- STRUCTURAL SIGNALS (ground truth from tool call log — these dims are computed deterministically; do NOT override):
- Schema travels **only via the flag**, never inside the prompt text.
- Schema compliance requires exact structure: {"schema_version": "attest-final-answer-semantic/v1", "claims": []}
- Sonnet model wraps JSON output in markdown code fences instead of returning bare JSON, violating schema requirement
- Opus model does not honor --json-schema flag; ignores it and returns prose instead of enforced JSON

## Eliminations / rejected
- Markdown-wrapped JSON output path is not viable; violates bare JSON schema requirement

## Premises (provisional)
- --json-schema CLI flag should enforce schema compliance and model output format across all models
