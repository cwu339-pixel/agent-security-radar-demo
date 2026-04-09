import json
from collections import defaultdict
from pathlib import Path


ALIAS_MAP = {
    "noma": "noma-security",
    "noma security": "noma-security",
    "noma-security": "noma-security",
    "witness ai": "witnessai",
    "witnessai": "witnessai",
    "adaptive": "adaptive-security",
    "adaptive security": "adaptive-security",
    "protect ai": "protect-ai",
    "protectai": "protect-ai",
    "cognition": "cognition",
    "cognition labs": "cognition",
}

DISPLAY_NAMES = {
    "noma-security": "Noma Security",
    "witnessai": "WitnessAI",
    "adaptive-security": "Adaptive Security",
    "protect-ai": "Protect AI",
    "cognition": "Cognition",
}

TAG_WEIGHTS = {
    "agent_security_focus": {"market": 8, "tech": 4},
    "enterprise_security": {"market": 3, "business": 3},
    "launch_signal": {"momentum": 4},
    "hiring_signal": {"business": 4, "momentum": 2},
    "team_security_background": {"team": 8},
    "team_ai_infra_background": {"team": 7},
    "github_activity": {"tech": 6, "momentum": 2},
    "technical_depth": {"tech": 6},
    "customer_signal": {"business": 8},
    "paper_or_blog": {"tech": 4},
    "momentum_signal": {"momentum": 5},
    "funding_signal": {"business": 6, "momentum": 2},
    "gtm_signal": {"business": 5},
    "open_source_signal": {"tech": 3},
    "ai_security_adjacent": {"market": 2},
    "agent_builder": {},
}

CORE_CATEGORY_HINTS = {
    "agent_runtime_security",
    "tool_permissioning",
    "agent_identity_access",
    "prompt_injection_defense",
    "policy_guardrails",
    "agent_observability_audit",
    "agent_sandboxing",
}

CATEGORY_LABELS = {
    "agent_runtime_security": "Agent Runtime Security",
    "tool_permissioning": "Tool Permissioning",
    "agent_identity_access": "Agent Identity & Access",
    "prompt_injection_defense": "Prompt Injection Defense",
    "policy_guardrails": "Policy Guardrails",
    "agent_observability_audit": "Agent Observability & Audit",
    "agent_sandboxing": "Agent Sandboxing",
    "adjacent_ai_security": "Adjacent AI Security",
    "out_of_scope": "Out of Scope",
}

FOLLOW_UP_QUESTIONS = {
    "team": "Do the founders have repeat security or AI infrastructure wins?",
    "market": "Is the company truly focused on agent security versus broader AI security?",
    "business": "Are there paying customers or only pilots and design partners?",
    "tech": "Is the technical moat visible in code, product docs, or research?",
    "momentum": "Is the recent activity sustained or just a single announcement spike?",
}


def load_signals(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def canonical_company_id(company_ref: str) -> str:
    key = company_ref.strip().lower()
    return ALIAS_MAP.get(key, key.replace(" ", "-"))


def build_company_cards(signals: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}

    for signal in signals:
        company_id = canonical_company_id(signal["company_ref"])
        card = grouped.setdefault(
            company_id,
            {
                "company_id": company_id,
                "display_name": DISPLAY_NAMES.get(company_id, signal["company_ref"]),
                "aliases_seen": set(),
                "evidence": [],
                "score_breakdown": defaultdict(int),
                "why_now": [],
                "category_hints": [],
            },
        )
        card["aliases_seen"].add(signal["company_ref"])
        card["evidence"].append(
            {
                "headline": signal["headline"],
                "source": signal["source"],
                "published_at": signal["published_at"],
                "url": signal["url"],
                "tags": signal["tags"],
            }
        )
        card["category_hints"].append(signal.get("category_hint", "out_of_scope"))

        for tag in signal["tags"]:
            for bucket, points in TAG_WEIGHTS.get(tag, {}).items():
                card["score_breakdown"][bucket] += points

        if "agent_security_focus" in signal["tags"]:
            card["why_now"].append("Directly framed around agent security use cases.")
        elif "customer_signal" in signal["tags"]:
            card["why_now"].append("Customer or partner evidence suggests commercial pull.")
        elif "funding_signal" in signal["tags"]:
            card["why_now"].append("Recent funding or financing signal suggests momentum.")

    cards: list[dict] = []
    for card in grouped.values():
        score_breakdown = dict(card["score_breakdown"])
        total_score = sum(score_breakdown.values())
        primary_category = select_primary_category(card["category_hints"])
        universe_tier = classify_universe_tier(primary_category)
        weakest_bucket = min(
            ["team", "market", "business", "tech", "momentum"],
            key=lambda bucket: score_breakdown.get(bucket, 0),
        )
        cards.append(
            {
                "company_id": card["company_id"],
                "display_name": card["display_name"],
                "aliases_seen": sorted(card["aliases_seen"]),
                "evidence": sorted(card["evidence"], key=lambda item: item["published_at"], reverse=True),
                "category": CATEGORY_LABELS.get(primary_category, primary_category.replace("_", " ").title()),
                "universe_tier": universe_tier,
                "score_breakdown": score_breakdown,
                "total_score": total_score,
                "why_now": dedupe_keep_order(card["why_now"])[:2],
                "unknowns": build_unknowns(score_breakdown, universe_tier),
                "follow_up_questions": [FOLLOW_UP_QUESTIONS[weakest_bucket]],
            }
        )
    return cards


def rank_companies(cards: list[dict]) -> list[dict]:
    tier_order = {"core": 2, "adjacent": 1, "out_of_scope": 0}
    return sorted(
        cards,
        key=lambda card: (
            tier_order.get(card["universe_tier"], -1),
            card["total_score"],
            card["score_breakdown"].get("market", 0),
            card["score_breakdown"].get("business", 0),
        ),
        reverse=True,
    )


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def select_primary_category(category_hints: list[str]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for hint in category_hints:
        counts[hint] += 1
    return max(counts, key=lambda hint: (counts[hint], hint))


def classify_universe_tier(primary_category: str) -> str:
    if primary_category in CORE_CATEGORY_HINTS:
        return "core"
    if primary_category == "adjacent_ai_security":
        return "adjacent"
    return "out_of_scope"


def build_unknowns(score_breakdown: dict[str, int], universe_tier: str) -> list[str]:
    unknowns: list[str] = []

    if score_breakdown.get("team", 0) < 6:
        unknowns.append("Founder and operator credibility still needs direct verification.")
    if score_breakdown.get("business", 0) < 10:
        unknowns.append("Commercial traction is still thin from public evidence.")
    if universe_tier == "adjacent":
        unknowns.append("Needs a sharper wedge into agent-native security, not just broader AI security.")
    if universe_tier == "out_of_scope":
        unknowns.append("This looks relevant to agents, but not to the agent security investment universe.")

    return unknowns[:2]
