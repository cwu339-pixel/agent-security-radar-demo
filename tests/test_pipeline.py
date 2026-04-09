import unittest
from pathlib import Path

from agent_security_radar.pipeline import build_company_cards, load_signals, rank_companies
from agent_security_radar.render import render_brief


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sample_signals.json"


class PipelineTests(unittest.TestCase):
    def test_aliases_are_merged_into_one_company_profile(self) -> None:
        signals = load_signals(DATA_PATH)
        cards = build_company_cards(signals)

        noma_card = next(card for card in cards if card["company_id"] == "noma-security")

        self.assertEqual(noma_card["display_name"], "Noma Security")
        self.assertIn("Noma", noma_card["aliases_seen"])
        self.assertGreaterEqual(len(noma_card["evidence"]), 3)

    def test_ranking_prefers_stronger_multi_signal_companies(self) -> None:
        signals = load_signals(DATA_PATH)
        ranked = rank_companies(build_company_cards(signals))

        names = [company["display_name"] for company in ranked[:3]]

        self.assertEqual(names[0], "Noma Security")
        self.assertIn("WitnessAI", names[:2])
        self.assertGreater(ranked[0]["total_score"], ranked[-1]["total_score"])

    def test_companies_are_labeled_by_universe_tier(self) -> None:
        signals = load_signals(DATA_PATH)
        cards = build_company_cards(signals)

        tiers = {card["display_name"]: card["universe_tier"] for card in cards}

        self.assertEqual(tiers["Noma Security"], "core")
        self.assertEqual(tiers["Protect AI"], "adjacent")
        self.assertEqual(tiers["Cognition"], "out_of_scope")

    def test_brief_contains_reasons_and_follow_up_questions(self) -> None:
        signals = load_signals(DATA_PATH)
        ranked = rank_companies(build_company_cards(signals))
        brief = render_brief(ranked, generated_on="2026-04-08")

        self.assertIn("重点候选公司", brief)
        self.assertIn("为什么现在值得看", brief)
        self.assertIn("目前还不知道什么", brief)
        self.assertIn("建议下一步追问", brief)


if __name__ == "__main__":
    unittest.main()
