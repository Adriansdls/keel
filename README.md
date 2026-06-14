# keel

**keel** makes Claude Code remember what matters across sessions — decisions, constraints, in-progress work — and automatically tracks everything you build.

## Install

```bash
git clone https://github.com/adriandelasierra/cowork
cd cowork
bash install.sh
```

That's it. Open Claude Code in any project and keel starts working.

**Requirements:** [Claude Code](https://claude.ai/code) and Python 3.9+. No API key needed — uses your Claude subscription.

---

## What happens automatically

Once installed, keel runs silently in the background on every Claude Code session:

- **Remembers decisions** — when you and Claude decide something, it's committed to memory and injected into every future session. Survives compaction and restarts.
- **Tracks work automatically** — tasks, bets, decisions captured from conversation without you asking.
- **Checks assumptions** — periodically validates that working assumptions are still true.
- **Watches for entropy** — notices when ideas pile up unacted on, projects go dark, or the field gets illegible.
- **Closes the loop** — retrospectively checks whether open bets have resolved and decisions are being honored.

---

## Project tools (available in every Claude session)

| Tool | What it does |
|---|---|
| `ra_boot` | Session start briefing — what's open, what's at risk |
| `ra_capture` | Track a new task or idea |
| `ra_decide` | Log a firm decision (with rejected alternatives) |
| `ra_bet` | Register a directional bet with confidence |
| `ra_advance` | Move an issue to a new status |
| `ra_brief` | Full strategic brief for a project |
| `ra_issues` | List open issues |
| `ra_prioritize` | Cross-project prioritization view |

---

## Works with Claude Cowork too

If you use the Claude desktop app (Claude Cowork), `install.sh` also registers ra-pm there automatically. Both Claude Code and Claude Cowork read and write the same `~/.keel/` store.

---

## Configuration

Edit `~/.keel/config.yaml` to change behaviour. Defaults work well out of the box.

```yaml
llm:
  mode: subscription   # uses your Claude subscription (default, no API key needed)
  # mode: api          # uses ANTHROPIC_API_KEY instead

memory:
  check_assumptions_every: 5
  max_inject_size: 12000

health:
  check_every_days: 7
  warn_if_idea_leakage_above: 0.40
```

---

## Your data

Everything lives in `~/.keel/` as plain YAML and JSONL files. Human-readable, no database, no cloud sync. You own it entirely.

---

## Update

```bash
cd cowork
git pull
bash install.sh   # safe to re-run anytime
```

## Uninstall

```bash
bash uninstall.sh           # removes hooks + MCP, keeps your data
bash uninstall.sh --purge   # removes everything
```
