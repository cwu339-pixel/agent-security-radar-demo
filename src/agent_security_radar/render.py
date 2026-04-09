from __future__ import annotations

TIER_LABELS = {
    "core": "核心目标池",
    "adjacent": "相邻观察池",
    "out_of_scope": "不在目标范围内",
}


def render_brief(ranked_companies: list[dict], generated_on: str) -> str:
    primary_candidates = [company for company in ranked_companies if company["universe_tier"] != "out_of_scope"]
    excluded_candidates = [company for company in ranked_companies if company["universe_tier"] == "out_of_scope"]

    lines = [
        "# Agent Security Radar 简报",
        "",
        f"生成日期：{generated_on}",
        "",
        "这份 MVP 主要证明一件事：代表性的多源信号可以被分类、归并成公司画像、完成打分，并输出成投资人可直接阅读的候选公司卡片。",
        "",
        "## 重点候选公司",
        "",
    ]

    for index, company in enumerate(primary_candidates, start=1):
        lines.append(f"### {index}. {company['display_name']} ({company['total_score']})")
        lines.append("")
        lines.append(f"- 目标池分层：{TIER_LABELS.get(company['universe_tier'], company['universe_tier'])}")
        lines.append(f"- 赛道类别：{company['category']}")
        lines.append("")
        lines.append("评分拆解：")
        for bucket in ["team", "market", "business", "tech", "momentum"]:
            lines.append(f"- {bucket}: {company['score_breakdown'].get(bucket, 0)}")
        lines.append("")
        lines.append("为什么现在值得看：")
        for reason in company["why_now"] or ["目前还缺少更直接的催化剂证据。"]:
            lines.append(f"- {reason}")
        lines.append("")
        lines.append("关键信息来源：")
        for item in company["evidence"][:3]:
            lines.append(f"- {item['published_at']} | {item['source']} | {item['headline']}")
        lines.append("")
        lines.append("目前还不知道什么：")
        for item in company["unknowns"] or ["这份 MVP 里暂未标记更多未知项。"]:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("建议下一步追问：")
        for question in company["follow_up_questions"]:
            lines.append(f"- {question}")
        lines.append("")

    if excluded_candidates:
        lines.append("## 不进入主目标池的对象")
        lines.append("")
        for company in excluded_candidates:
            lines.append(f"### {company['display_name']}")
            lines.append("")
            lines.append(f"- 目标池分层：{TIER_LABELS.get(company['universe_tier'], company['universe_tier'])}")
            lines.append(f"- 赛道类别：{company['category']}")
            lines.append("- 原因：和 agent 有关，但不属于 agent security 投资范围。")
            lines.append("")

    return "\n".join(lines).strip() + "\n"
