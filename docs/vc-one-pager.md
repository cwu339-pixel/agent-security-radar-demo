# VC 一页纸

## 问题

一个关注 Agent Security 赛道的投资团队，通常会遇到四个问题：

- 目标池边界不清楚
- 新公司发现得不够早，也不稳定
- 证据分散在不同来源里
- 分析师的注意力浪费在低优先级名字上

真正的问题不是“能不能搜到网页”，而是：

> 怎么把嘈杂的公开信号，变成一份可解释、可行动的投资 shortlist？

## 为什么是现在

Agent 安全正在逐渐成为 AI 基础设施和企业安全里的独立问题域。随着 agent 拿到工具调用、记忆、权限和执行能力，新的公司类型正在出现，例如：

- runtime control
- prompt / tool injection defense
- policy enforcement
- agent identity and access
- observability and audit
- sandboxing

这意味着很多相关公司会先出现在社交媒体、招聘页、技术博客、开源仓库和研究资料里，而不是先出现在标准数据库里。

## 这个系统给投资团队带来什么

这套系统不是做内容摘要，而是做 VC workflow 支持。

它帮助投资团队：

- 定义什么公司属于 Agent Security 目标池
- 持续发现新候选公司
- 把零散证据整理成公司画像
- 用可解释的规则完成排序
- 给分析师一份带有 `why now`、`unknowns` 和 `follow-up questions` 的 shortlist

## MVP 证明什么

这个 MVP 不用真实线上数据，主要证明 workflow 的逻辑成立：

- 代表性多源信号可以被统一表示
- 公司别名可以归并
- 公司可以被标记为 `core`、`adjacent` 或 `out_of_scope`
- 候选公司卡片可以被自动生成，且适合投资场景阅读

## 明确不在这次范围里的内容

这份交付故意不包含：

- 付费或受限数据源的真实抓取
- 完整 7x24 编排
- 线上 LLM 抽取稳定性
- CRM 集成
- 生产级 dashboard

这些属于后续扩展。当前面试更重要的是证明：这套 workflow 是清楚的，而且对 VC 团队有用。
