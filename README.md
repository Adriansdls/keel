# cowork

**cowork** makes Claude Code remember what matters across sessions — decisions, constraints, in-progress work — and automatically tracks everything you build.

## Install

```bash
git clone https://github.com/YOUR_USERNAME/cowork
cd cowork
bash install.sh
```

That's it. Open Claude Code in any project and cowork starts working.

**Requirements:** [Claude Code](https://claude.ai/code) and Python 3.9+. No API key needed.

## What happens automatically

Once installed, cowork runs silently in the background on every Claude Code session:

- **Remembers decisions** — when you and Claude decide something (pick a tech, reject an approach, set a constraint), it's remembered across sessions and even after compaction
- **Tracks work** — tasks, bets, and decisions are automatically captured in a project tracker you can query anytime
- **Checks assumptions** — periodically validates that working assumptions are still true given what's happened recently
- **Bridges sessions** — nothing is lost when a session ends or the context window compacts

## Project management tools (available in any Claude session)

Call these directly or ask Claude to call them:

| Tool | What it does |
|---|---|
| `ra_capture` | Track a new task or idea |
| `ra_decide` | Log a firm decision (with rejected alternatives) |
| `ra_bet` | Register a directional bet with confidence |
| `ra_advance` | Move an issue to a new status |
| `ra_brief` | Get a full strategic brief for a project |
| `ra_issues` | List open issues for a project |
| `ra_boot` | Session start briefing — what's open, what's at risk |

## Configuration

Edit `~/.cowork/config.yaml` to change behaviour. The defaults work well — you probably don't need to touch this.

```yaml
llm:
  mode: subscription   # uses your Claude subscription (default)
  # mode: api          # uses ANTHROPIC_API_KEY instead

memory:
  check_assumptions_every: 5   # turns between premise checks
  max_inject_size: 12000        # characters injected per turn

health:
  check_every_days: 7          # how often to review project health
```

## Update

```bash
cd cowork
git pull
bash install.sh   # re-running is always safe
```

## Uninstall

```bash
bash uninstall.sh           # removes hooks + MCP, keeps your data
bash uninstall.sh --purge   # removes everything including data
```

## Your data

Everything cowork stores lives in `~/.cowork/`. It's plain YAML and JSONL files — human-readable, no database, no cloud sync. You own it.
