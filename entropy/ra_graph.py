"""ra_graph — model the ra-pm corpus as a simple graph for connectivity scoring.

Replaces the original evidence_gate.graph.VaultGraph dependency with a
self-contained SimpleGraph. Same metrics, zero external dependencies.

Nodes: projects (P), ideas (I), issues (S), decisions (D)
Edges encode the value-trace:
  idea   → project      (routed)
  issue  → project      (belongs to)
  issue  → idea         (from_idea lineage)
  decision → project    (logged in)

Connectivity = fraction of nodes with at least one edge.
A connected corpus means ideas are traceable to work; isolated dust = unharvested entropy.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared import store


class SimpleGraph:
    """Minimal undirected graph: adjacency list + degree queries."""

    def __init__(self) -> None:
        self._adj: dict[str, set[str]] = defaultdict(set)

    def add_node(self, node_id: str) -> None:
        if node_id not in self._adj:
            self._adj[node_id] = set()

    def add_edge(self, a: str, b: str) -> None:
        self.add_node(a)
        self.add_node(b)
        self._adj[a].add(b)
        self._adj[b].add(a)

    def degree(self, node_id: str) -> int:
        return len(self._adj.get(node_id, set()))

    def number_of_nodes(self) -> int:
        return len(self._adj)

    def connectivity(self) -> float:
        """Fraction of nodes with degree ≥ 1 (i.e. not isolated)."""
        n = self.number_of_nodes()
        if n == 0:
            return 0.0
        connected = sum(1 for nbrs in self._adj.values() if nbrs)
        return round(connected / n, 3)


def build_ra_graph() -> tuple[dict, SimpleGraph, dict]:
    """
    Returns (node_index{code: metadata}, SimpleGraph, refs).
    refs maps semantic keys → node codes for external lookups.
    Uses shared.store — reads $KEEL_HOME/ra/.
    """
    projects  = store.load_projects()
    ideas     = store.load_ideas()

    proj_code = {p.id: f"P{i+1}" for i, p in enumerate(projects)}
    refs: dict[str, dict] = {"project": proj_code, "idea": {}, "issue": {}, "decision": {}}
    node_index: dict[str, dict] = {}
    g = SimpleGraph()

    # Projects
    for p in projects:
        code = proj_code[p.id]
        node_index[code] = {"type": "project", "id": p.id, "name": p.name}
        g.add_node(code)

    # Ideas (edge → their project if routed)
    for i, idea in enumerate(ideas):
        code = f"I{i+1}"
        refs["idea"][i] = code
        node_index[code] = {"type": "idea", "title": idea.title, "project": idea.project}
        g.add_node(code)
        tgt = proj_code.get(idea.project or "")
        if tgt:
            g.add_edge(code, tgt)

    # Issues + decisions per project
    sc = dc = 0
    for p in projects:
        pcode = proj_code[p.id]
        for iss in store.load_issues(p.id):
            sc += 1
            code = f"S{sc}"
            refs["issue"][(p.id, iss.id)] = code
            node_index[code] = {"type": "issue", "title": iss.title, "project": p.id}
            g.add_edge(code, pcode)
            # from_idea lineage edge
            fi = iss.from_idea
            if fi is not None and fi in refs["idea"]:
                g.add_edge(code, refs["idea"][fi])
        for dec in store.load_decisions(p.id):
            dc += 1
            code = f"D{dc}"
            refs["decision"][(p.id, dec.id)] = code
            node_index[code] = {"type": "decision", "decision": dec.decision, "project": p.id}
            g.add_edge(code, pcode)

    return node_index, g, refs
