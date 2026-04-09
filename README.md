# Agent Security Radar

A continuous investment research pipeline that scans the Agent Security landscape and outputs investor-ready company shortlists.

## What This Does

```
Source Signals → Relevance Classification → Company Profiles → Scoring → Investment Shortlist
```

The system:
1. **Collects** signals from GitHub, X/Twitter, Reddit, Hacker News
2. **Classifies** each signal for agent security relevance (core / adjacent / out_of_scope)
3. **Merges** multi-source signals into unified company profiles with entity resolution
4. **Scores** companies across 5 dimensions: team, market, business, tech, momentum
5. **Outputs** ranked shortlist with evidence, unknowns, and follow-up questions

## Quick Start

### Demo Mode (no API key needed)

Runs the full pipeline with representative sample data:

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m agent_security_radar.cli demo
```

### Live Scan Mode (requires OpenAI API key)

Scrapes real sources and uses LLM to classify signals:

```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

PYTHONPATH=src python -m agent_security_radar.cli scan
PYTHONPATH=src python -m agent_security_radar.cli scan --sources github hackernews
PYTHONPATH=src python -m agent_security_radar.cli scan --max 10
```

### Run Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Output

### Outputs Generated

- `outputs/ranking.json` — structured company data with scores and evidence
- `outputs/daily_brief.md` — investor-facing markdown brief

### Example Output

```
### 1. Noma Security (75)
- Universe tier: core
- Category: Agent Runtime Security

Score breakdown:
- team: 8 | market: 19 | business: 15 | tech: 20 | momentum: 13

Why now:
- Directly framed around agent security use cases.

Unknowns:
- Founder and operator credibility still needs direct verification.

Follow-up questions:
- Do the founders have repeat security or AI infrastructure wins?
```

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Scrapers    │────>│  Classifier  │────>│  Company Profile │
│              │     │  (LLM-based) │     │     Builder       │
│ · GitHub     │     │              │     └────────┬─────────┘
│ · X/Twitter  │     │ · relevance  │              │
│ · Reddit     │     │ · tagging    │     ┌────────▼─────────┐
│ · HackerNews │     │ · scoping    │     │  Scoring Engine   │
└──────────────┘     └──────────────┘     └────────┬─────────┘
                                                   │
                                          ┌────────▼─────────┐
                                          │  Shortlist Output │
                                          │  (investor-ready) │
                                          └──────────────────┘
```

## Investment Universe

| Tier | Definition | Examples |
|------|-----------|---------|
| **Core** | Directly building agent security products | Runtime guardrails, agent auth, sandbox, prompt injection defense |
| **Adjacent** | Related but not pure-play agent security | General AI security, model scanning, LLM firewalls |
| **Out of Scope** | No agent security angle | Traditional cybersecurity, agent builders without security focus |

## Scoring Dimensions

| Dimension | Signals |
|-----------|---------|
| **Team** | Founder background, security expertise, key hires |
| **Market** | Agent security focus, TAM relevance, timing |
| **Business** | Customer traction, funding, GTM signals |
| **Tech** | GitHub activity, technical depth, open source |
| **Momentum** | Recent activity, media coverage, hiring |

Every score traces back to specific evidence. No score without a receipt.

## Project Structure

```
├── src/agent_security_radar/
│   ├── pipeline.py          # Core: scoring, entity resolution, ranking
│   ├── render.py            # Markdown brief generation
│   ├── cli.py               # CLI entry point (demo + live scan)
│   ├── scrapers/            # Data collection from 4 sources
│   ├── analyzer/            # LLM classifier + event deduplication
│   └── models/              # ContentItem data model
├── data/sample_signals.json # Representative sample data
├── outputs/                 # Generated briefs and rankings
├── tests/                   # Unit tests
└── docs/                    # Design documents
```

## Design Document

See [docs/direct-share-summary.md](docs/direct-share-summary.md) for the full design rationale, tradeoffs, and MVP scope.
