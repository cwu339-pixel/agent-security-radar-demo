from __future__ import annotations


def render_brief(ranked_companies: list[dict], generated_on: str) -> str:
    primary_candidates = [company for company in ranked_companies if company["universe_tier"] != "out_of_scope"]
    excluded_candidates = [company for company in ranked_companies if company["universe_tier"] == "out_of_scope"]

    lines = [
        "# Agent Security Radar Brief",
        "",
        f"Generated on: {generated_on}",
        "",
        "This MVP demonstrates a VC workflow proof: representative multi-source signals are classified, merged into company profiles, scored, and translated into investor-facing candidate cards.",
        "",
        "## Top Candidates",
        "",
    ]

    for index, company in enumerate(primary_candidates, start=1):
        lines.append(f"### {index}. {company['display_name']} ({company['total_score']})")
        lines.append("")
        lines.append(f"- Universe tier: {company['universe_tier']}")
        lines.append(f"- Category: {company['category']}")
        lines.append("")
        lines.append("Score breakdown:")
        for bucket in ["team", "market", "business", "tech", "momentum"]:
            lines.append(f"- {bucket}: {company['score_breakdown'].get(bucket, 0)}")
        lines.append("")
        lines.append("Why now:")
        for reason in company["why_now"] or ["Needs more direct catalyst evidence."]:
            lines.append(f"- {reason}")
        lines.append("")
        lines.append("Evidence:")
        for item in company["evidence"][:3]:
            lines.append(f"- {item['published_at']} | {item['source']} | {item['headline']}")
        lines.append("")
        lines.append("Unknowns:")
        for item in company["unknowns"] or ["No additional unknowns flagged in this MVP."]:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("Follow-up questions:")
        for question in company["follow_up_questions"]:
            lines.append(f"- {question}")
        lines.append("")

    if excluded_candidates:
        lines.append("## Excluded From Primary Universe")
        lines.append("")
        for company in excluded_candidates:
            lines.append(f"### {company['display_name']}")
            lines.append("")
            lines.append(f"- Universe tier: {company['universe_tier']}")
            lines.append(f"- Category: {company['category']}")
            lines.append("- Reason: relevant to agents, but not to the agent security investment universe.")
            lines.append("")

    return "\n".join(lines).strip() + "\n"
