#!/usr/bin/env python3
import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent_security_radar.pipeline import build_company_cards, load_signals, rank_companies
from agent_security_radar.render import render_brief


def main() -> None:
    signals = load_signals(ROOT / "data" / "sample_signals.json")
    ranked = rank_companies(build_company_cards(signals))

    outputs_dir = ROOT / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    (outputs_dir / "ranking.json").write_text(json.dumps(ranked, indent=2))
    (outputs_dir / "daily_brief.md").write_text(
        render_brief(ranked, generated_on=str(date.today()))
    )
    print(f"Wrote {outputs_dir / 'ranking.json'}")
    print(f"Wrote {outputs_dir / 'daily_brief.md'}")


if __name__ == "__main__":
    main()
