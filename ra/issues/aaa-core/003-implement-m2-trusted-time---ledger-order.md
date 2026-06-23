---
id: 3
title: Implement M2 trusted-time / ledger-order freshness, replacing M1 wall-clock
  TTL
status: idea
priority: p1
area: dev
why: 'threat-model.md marks clock-skew-defeats-freshness as partial in M1: an attacked
  host clock defeats the wall-clock TTL, which is load-bearing for stale-evidence-fails-closed.
  Freshness must rest on a non-attackable source before any real deployment.'
created: '2026-06-23'
updated: '2026-06-23'
---

