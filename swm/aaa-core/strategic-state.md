# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- Reconciler marks stranded `consumed_pending` → `consumed_unknown`, never back to `issued`.
- Never output tokens in plaintext." — no task overrides this.
- Never output tokens in plaintext." The leaked `gho_` token must NEVER be reproduced.
- Never (forbidden): commit_or_print_secrets, force_push_default_branch, disable_or_bypass_governance.
- Please do not reproduce the token anywhere.
- MUST NOT rotate without Adrian's explicit in-context confirmation.
- Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar.
- Pick up the last task as if the break never happened.
- One approval cannot mint two leases for different actions; reusable CI evidence may satisfy multiple compatible actions.
- Do not turn legitimate reconciliation retries into crashes.
- Do not begin M2B until the post-fix PIMS catalog is green and its scope/limitations are documented."
- refuse_rate = `refused / (refused + escaped + crashed)` over MUST_REFUSE; outcomes REFUSED/ESCAPED/CRASHED/NOT_APPLICABLE/REGRESSION; reporting scoped "declared M2 mutation catalog", never universal coverage.
- Do NOT call any tools..." — the summary request itself.)
- Note gateway never applies `skew_seconds` to the lease-expiry check.
- The signed payload is `canonical_json(self.claims.model_dump())` — claims do NOT include `sig_key_id` or `sig_value`, so `sig_key_id` is NOT covered by the signature.
- Never returns a lease to `issued`.
- `"credential isolation at the downstream effect boundary (gateway holds deploy token; agent never receives it)"`
- Please propose an OSS licence separately; do not assume one."
- Model text is NEVER evidence.
- `reconcile(now, deadline_seconds)` marks stranded pending → consumed_unknown (never → issued).
- Token private, never exposed.
- MUST NOT reproduce token.
- Do not auto-proceed to M2 or rotate the token without Adrian's explicit in-context decision.

## Eliminations / rejected
- The first transition succeeds; an identical retry returns the existing outcome; a conflicting outcome after a terminal state is rejected.
- **TX1** (lines 142–145): `attempt = self.lease_store.consume(lease, now=now, consumer_host=consumer_host)`; `except ConsumeRejection as e: raise LeaseConsumeError(f"consume rejected: {e}") from e`.
- `test_replay_rejected` — execute twice; second raises `LeaseConsumeError("consume rejected")`; asserts `adapter.execution_count == 1` and `store_state(gateway, lease.lease_id) == STATE_CONSUMED_SUCCESS`.
- `test_altered_payload_rejected` — issue for `COMMIT`, execute with `make_env(commit_sha="zzz999")`; expects `LeaseConsumeError("action_digest")`.
- `test_wrong_target_adapter_rejected` — build a second gateway via `_clone_gateway(gateway, adapter=other_adapter)` with `MockDeployAdapter(adapter_id="other-deploy")`; expects `LeaseConsumeError("audience")`.
- `test_wrong_environment_rejected` — issue for `production`, execute with `staging`; `LeaseConsumeError("action_digest")`.
- `test_wrong_tenant_rejected` — same pattern with `tenant="other-tenant"`.

## Premises (provisional)
- Pending Tasks:
- Then insert `execution_attempts` (lines 327–334) with `attempt_id`, `lease_id`, `idempotency_key=idem`, `started_at=now_iso()`, `started_epoch=now`, `state="pending"`.
- Updates `leases` → `STATE_CONSUMED_UNKNOWN` where `state = STATE_CONSUMED_PENDING` and lease_id in (attempts with `state='pending' AND started_epoch &lt; cutoff`).
- Then updates `execution_attempts` → `state='unknown'`, `completed_at=now_iso()` where `state='pending' AND started_epoch &lt; cutoff`.
