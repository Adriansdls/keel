"""Cold log + recall — the third leg of the memory hierarchy.

An append-only, NEVER-pruned full transcript per session (the cold store), plus recall(query)
to fetch original turns on demand. This is what makes aggressive window-pruning safe: nothing
is ever truly lost — when the user says "but I told you X," recall() retrieves the verbatim turn
from the cold store. Grep-scored by default; optional Ollama-embedding rerank.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

# Default; rebound to a per-project dir via configure() when installed globally.
COLD_DIR = Path(__file__).resolve().parent.parent / "cold-logs"
_WORD = re.compile(r"[a-z0-9$]+")


def configure(cold_dir) -> None:
    """Point the cold store at a per-project directory (set by the hook entrypoints)."""
    global COLD_DIR
    COLD_DIR = Path(cold_dir)
_STOP = {"the", "a", "an", "is", "are", "of", "to", "and", "we", "i", "it", "that", "this",
         "what", "did", "you", "me", "my", "our", "about", "for", "but", "told", "said", "was"}


def _terms(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if len(w) > 2 and w not in _STOP}


def append(session_id: str, role: str, text: str, turn: int = -1) -> None:
    """Append a turn to the append-only cold store (never pruned)."""
    if not text.strip():
        return
    COLD_DIR.mkdir(parents=True, exist_ok=True)
    rec = {"ts": time.time(), "turn": turn, "role": role, "text": text}
    with (COLD_DIR / f"{session_id}.jsonl").open("a") as f:
        f.write(json.dumps(rec) + "\n")


def _load(session_id: str | None) -> list[dict]:
    files = [COLD_DIR / f"{session_id}.jsonl"] if session_id else sorted(COLD_DIR.glob("*.jsonl"))
    out = []
    for fp in files:
        if fp.exists():
            for line in fp.read_text().splitlines():
                if line.strip():
                    try:
                        out.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return out


def recall(query: str, session_id: str | None = None, k: int = 5) -> list[dict]:
    """Return the top-k cold-store turns most relevant to query (grep-scored)."""
    q = _terms(query)
    if not q:
        return []
    scored = []
    for rec in _load(session_id):
        overlap = len(q & _terms(rec.get("text", "")))
        if overlap:
            scored.append((overlap, rec))
    scored.sort(key=lambda x: (-x[0], -x[1].get("ts", 0)))
    return [{"turn": r.get("turn"), "role": r["role"], "score": s, "text": r["text"]} for s, r in scored[:k]]


# heuristic: does a user turn ask to retrieve something from earlier?
_RECALL_INTENT = re.compile(
    r"\b(you told me|i told you|i mentioned|i said|earlier|recall|retrieve|remember when|what did i say|"
    r"go back to|we discussed|as i said|that thing about)\b", re.I)


def wants_recall(user_text: str) -> bool:
    return bool(_RECALL_INTENT.search(user_text))


if __name__ == "__main__":
    import sys
    for hit in recall(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None):
        print(f"[t{hit['turn']} {hit['role']} score={hit['score']}] {hit['text'][:120]}")
