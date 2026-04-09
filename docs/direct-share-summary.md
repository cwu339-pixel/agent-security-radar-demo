# Agent Security Radar — 设计思路

## 1. 问题理解

需求：构建一个持续扫描 Agent Security 领域的系统，最终输出一份投资团队可直接使用的 shortlist。

在进入架构之前，先明确这个系统**不是什么**：

- 不是一个爬虫，把数据堆进表格就完事
- 不是一份一次性的研究报告

它是一套**持续运行的投研 workflow** —— 核心价值在于把零散信号转化为结构化的、有排序的公司画像，让投资团队可以直接行动。

关键认知：难点不在"抓更多数据"，而在于**判断什么值得关注**、**正确归并证据**、**让输出可执行**。

## 2. 核心设计决策

### 决策 1：先定边界，再抓数据

一个常见的做法是：先把所有东西都抓过来，然后再筛。但这会引入大量噪音，下游全部受污染。

我的做法是先定义目标池（target universe），把公司分成三个层级：

| 层级 | 定义 | 举例 |
|------|------|------|
| **Core** | 直接做 agent security 产品的公司 | Runtime guardrails、agent auth、sandbox tooling |
| **Adjacent** | 相关但不是纯 agent security | 通用 AI security、带 agent 功能的基础设施 |
| **Out of Scope** | 没有实质性 agent security 角度 | 传统网络安全、无关 AI 公司 |

**为什么这么做**：下游所有环节（打分、排序、输出）都依赖于干净的 scoping。如果目标池被污染，shortlist 就没有意义。

### 决策 2：以 Company Profile 为中心实体

信号来自很多源头（X、LinkedIn、GitHub、新闻、论文、产品文档）。直觉上可能会按来源存一堆 signal list，但这样没法回答：*"我们对 X 公司到底了解多少？"*

所以系统的核心是把所有信号归并到**统一的公司画像**下：

```
Company Profile
├── company_name
├── tier: core | adjacent
├── category: 比如 runtime guardrails, agent auth
├── evidence[]: 带时间戳，带来源链接
├── recent_changes[]: 上次扫描以来发生了什么变化
├── unknowns[]: 我们还不知道什么
└── scores: { team, market, business, tech, momentum }
```

**归并（merge）是整个系统最难的一步。** 跨多个噪音源做 entity resolution 是大部分 pipeline 崩掉的地方。我的方案：

1. 公司名标准化（fuzzy matching + 别名表）
2. 证据去重（不同来源说的是同一件事 = 只保留一条 evidence）
3. 所有内容带时间戳 —— 时效性直接影响 momentum 打分

### 决策 3：可解释的打分，而不是黑盒排序

打分用五个维度：

| 维度 | 衡量什么 |
|------|---------|
| **Team** | 创始人背景、招聘信号、关键人才 |
| **Market** | TAM 相关性、时机、监管顺风 |
| **Business** | 收入信号、客户 traction、合作伙伴 |
| **Tech** | 产品深度、差异化、开源活跃度 |
| **Momentum** | 近期融资、媒体曝光、增长信号 |

**设计原则**：每一个分数都必须能追溯到具体的 evidence。没有证据就没有分数。

这一点不能妥协，因为使用者是投资团队 —— 他们需要能质疑、能验证，而不是盲信一个数字。

### 决策 4：基于调度器的持续运行，而不是单一常驻进程

"7x24" 不意味着一个永远跑着的进程，那太脆弱了。

合理的设计是：
- **Scheduler** 按可配置的间隔分发采集任务
- **Queue** 解耦任务创建和执行
- **Workers** 负责抓取、分类、归并、打分
- **Database** 持久化公司画像和证据
- **Heartbeat monitor** 检查 worker 存活和数据源健康度

**为什么不用简单的 cron？** 因为不同数据源有不同的最优轮询频率（GitHub：每天一次，X：每小时，新闻：几小时一次），而且需要在某个源变慢或被限流时做 backpressure 处理。

## 3. 系统流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Scheduler   │────>│   Workers    │────>│  Company Profile │
│ (按数据源    │     │              │     │     Database      │
│  分别调度)   │     │ 1. Collect   │     └────────┬─────────┘
└──────────────┘     │ 2. Classify  │              │
                     │ 3. Merge     │     ┌────────▼─────────┐
                     │ 4. Score     │     │  Scoring Engine   │
                     └──────────────┘     └────────┬─────────┘
                                                   │
                                          ┌────────▼─────────┐
                                          │  Shortlist Output │
                                          │  (investor-ready) │
                                          └──────────────────┘
```

**Step 1 → 采集**：从配置好的数据源拉取新内容，统一成标准 schema。

**Step 2 → 分类**：判断这条信号是否属于 Agent Security 目标池，标记为 core / adjacent / out_of_scope。这一步用 LLM 做分类，配合定义好的 prompt 和 few-shot examples。

**Step 3 → 归并**：做 entity resolution、去重，追加到对应的 company profile。这是最容易出错的一步，需要详细的日志记录。

**Step 4 → 打分**：基于更新后的证据重新评估分数。分数是增量式的 —— 新证据调整已有分数，而不是覆盖。

**Step 5 → 输出**：生成 shortlist。只呈现超过相关性阈值的公司，重点突出有显著变化的和新进入的。

## 4. 输出格式

最终输出面向投资团队，不是面向工程师。

每张公司卡片包含：

| 字段 | 作用 |
|------|------|
| Company Name | 公司名 |
| Tier | Core 还是 Adjacent |
| Category | 在 agent security 里做什么 |
| Score Breakdown | 5 个维度，每个维度附带证据链接 |
| Why Now | 最近发生了什么变化让这家公司值得关注 |
| Key Evidence | 最有说服力的 3-5 条信号 |
| Unknowns | 我们无法验证的部分 |
| Follow-up Questions | 建议人工进一步调研的方向 |

输出分三个板块：
- **Top Candidates** —— 评分最高、最值得行动的
- **New Entrants** —— 新发现、尚未充分评估的
- **Meaningful Changes** —— 已有公司中发生了显著变化的

## 5. 方案取舍

| 问题 | 我的选择 | 备选方案 | 为什么 |
|------|---------|---------|-------|
| 目标池定义 | 人工 taxonomy + LLM 分类 | 全自动聚类 | 投资场景下精确度比召回率重要 |
| Entity resolution | Fuzzy match + 别名表 | Knowledge graph | 更简单，公司数 <1000 时够用，后续可升级 |
| 打分模型 | 规则驱动 + 证据链接 | ML 排序 | 可解释性是硬性要求 |
| 轮询策略 | 按数据源分别调度 | 实时 streaming | 大部分源不支持 streaming，polling 更务实 |

**核心风险**：Entity resolution 的错误会累积。如果两家公司被错误合并，它们的分数都会被污染。应对措施：低置信度的合并标记为待人工确认。

## 6. MVP 要证明什么

MVP 不需要是一个生产级系统。它只需要证明一件事：

> **零散的原始信号可以被自动转化成一份带可追溯证据的、投资可用的 shortlist。**

具体来说，MVP 跑通这条链路就够了：

```
数据源信号 → 相关性分类 → 公司画像 → 打分 → shortlist
```

MVP 范围：
- 2-3 个数据源（比如 X + GitHub + 一个新闻 API）
- 约 20-30 家种子公司
- 基础 entity resolution（精确匹配 + fuzzy name match）
- 规则驱动打分，权重手动调
- 输出为结构化 JSON 或 markdown 卡片

明确后置的：
- 实时 streaming
- 高级 entity resolution（knowledge graph）
- UI / Dashboard
- 多用户权限控制
