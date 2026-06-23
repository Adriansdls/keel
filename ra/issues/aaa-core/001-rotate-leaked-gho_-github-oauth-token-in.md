---
id: 1
title: Rotate leaked gho_ GitHub OAuth token in the cc-os adrianzartis git remote
  (loca
status: idea
priority: p0
area: infra
why: 'A leaked OAuth token with write access to the adrianzartis org is a standing
  credential-exposure risk. Even though it currently lives only in local git config
  (not committed), the token itself is live and reusable if exfiltrated from this
  machine. Adrian has deferred this; tracking it as an open issue so it does not become
  invisible. It is also directly relevant to aaa-core''s credibility: a project whose
  thesis is ''agent actions are safe because credentials are isolated'' cannot sit
  on a leaked credential.'
hypothesis: Rotating the token + updating the local remote + revoking the old token
  at GitHub leaves no live credential on disk and breaks nothing in the aaa-core push
  path.
created: '2026-06-23'
updated: '2026-06-23'
---

