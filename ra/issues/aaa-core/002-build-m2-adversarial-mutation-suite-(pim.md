---
id: 2
title: Build M2 adversarial mutation suite (PIMS) at the effect boundary + aggregator
status: idea
priority: p1
area: dev
why: This is the proof instrument for the project thesis and tests bet 3. M1 functional
  tests pass, but functional coverage under-claims the actual boundary; without a
  mutation suite there is no honest refuse-rate signal and the security claim rests
  on assertion, not proof. This is the single highest-leverage M2 item.
hypothesis: Running PIMS against M1 reveals >=1 escape that the M1 functional tests
  miss, confirming that functional-test-pass is not a valid security claim for this
  boundary.
created: '2026-06-23'
updated: '2026-06-23'
---

