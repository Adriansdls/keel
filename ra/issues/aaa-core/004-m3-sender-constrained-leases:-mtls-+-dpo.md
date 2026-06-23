---
id: 4
title: 'M3 sender-constrained leases: mTLS + DPoP-style proof-of-possession (RFC 9449)
  t'
status: idea
priority: p1
area: dev
why: The two explicitly NOT-protected M1 gaps in what-is-protected.md. Without sender
  binding, a stolen lease wins the race to first use, which breaks the boundary claim
  in any topology where the agent environment is not fully trusted. Tests bet 5.
created: '2026-06-23'
updated: '2026-06-23'
---

