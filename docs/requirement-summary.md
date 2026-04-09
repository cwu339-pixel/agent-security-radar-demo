# Agent Security Interview Prompt: Requirement Summary And Working Interpretation

## 1. Original Prompt

根据面试题截图，题目核心是：

> 设计一个 Agent，能够 7x24 小时不间断扫描值得投资的 Agent 安全公司。  
> 信息源可以包括公众号、PitchBook、The Information、Twitter、Reddit、LinkedIn、论文等。  
> 检索后，需要通过团队背景、业务数据等信息进行评分排序。  
> 可以提交各种类型文档和 GitHub 代码。  
> 重点主要体现思路，项目结果次要。

## 2. What The Interviewer Is Actually Testing

这题表面上像“做一个情报 Agent”，但本质上更像一道：

- 投资研究工作流设计题
- Agent 系统拆解题
- 多源情报归并与排序题

面试官更在意的不是你能不能短时间做出完整产品，而是你是否能清楚回答下面几个问题：

1. 目标到底是什么
2. 目标池怎么定义
3. 信息源为什么这样选
4. 抓回来的信息怎么归并
5. 排序逻辑怎么做到可解释
6. 最终输出如何真正服务投资决策

## 3. Requirement Clarification

### 3.1 This Is Not Just A News Summarizer

如果把题目理解成“每天搜新闻然后生成一份 summary”，理解就偏了。

更准确的目标应该是：

> 设计一个持续运行的 sourcing system，持续发现、验证、归并、排序值得关注的 Agent 安全公司，并把优先级最高的机会推给投资人。

所以最终交付不应该只是日报，而应该包括：

- 新发现的候选公司
- 已有公司的重要变化
- 当前最值得优先看的 Top list

### 3.2 The Hard Part Is Not Search, But Definition And Aggregation

这道题最关键的两步不是“抓很多来源”，而是：

1. 先定义什么是 `Agent 安全相关公司`
2. 再把分散在不同来源中的信号归并成统一公司画像

如果不先定义目标池，系统会把大量泛 AI security、传统 security、只是用了 AI 做营销的公司混进来。

如果没有公司画像层，系统会出现：

- 同一家公司被算成多个对象
- 分数无法累积
- 结论无法追溯
- 输出缺少可信度

## 4. Working Interpretation Of The Scope

### 4.1 What Counts As An Agent Security Company

目前推荐的工作定义如下：

> Agent 安全公司，是指那些专门解决 AI agent 在自主调用工具、访问数据、执行动作、与外部系统交互过程中产生的新型安全、权限、治理、审计或隔离问题的公司。

这个定义强调的是：

- protecting AI agents
- controlling agent behavior
- governing tool usage and permissions
- preventing prompt injection / tool misuse
- monitoring or auditing agent actions

它不等于：

- using AI for security
- general AI security
- traditional cybersecurity with AI branding

### 4.2 Universe Segmentation

为了让筛选稳定，建议把目标池分成三层：

#### Core Agent Security

直接围绕 agent 行为控制、防护、治理、隔离、审计的公司，例如：

- agent runtime security
- tool permissioning
- prompt injection defense
- agent identity and access control
- policy guardrails
- agent monitoring and audit
- agent sandboxing

这部分进入主 ranking。

#### Adjacent AI Security

与 AI security 强相关，但不一定直接聚焦 agent-native 风险，例如：

- LLM firewall
- model governance
- model risk and compliance
- AI data leakage prevention
- AI supply chain security

这部分进入 watchlist，不建议和 core companies 混成一个主榜单。

#### Out Of Scope

应主动排除：

- 传统安全公司，只是包装 AI 能力
- 泛 AI 应用公司，没有安全产品
- 纯研究团队，没有公司化产品
- 只做模型效果优化，不做控制和防护

## 5. Proposed System Understanding

当前推荐把系统理解为一个六层流水线，而不是一个聊天机器人。

### Layer 1: Source Ingestion

为不同来源建立 adapter，定时抓取新内容，统一存成标准 `raw signal`。

每条 raw signal 至少包含：

- source
- url
- published_at
- raw_text
- title
- metadata

### Layer 2: Relevance Filtering

先做低成本过滤，只保留和 Agent 安全目标池高相关的内容。

过滤方式可以组合：

- keyword rules
- taxonomy match
- embedding similarity
- source weighting

### Layer 3: Structured Extraction

用 LLM 从文本中抽结构化字段，而不是直接让它判断值不值得投。

提取内容包括：

- company_name
- aliases
- category
- summary
- founder/team hints
- customer/funding/hiring/github/paper signals
- confidence

### Layer 4: Entity Resolution / Company Profile Layer

把不同来源对同一公司的提及合并到一个 company profile 下。

company profile 至少应包含：

- canonical name
- aliases
- website / GitHub / LinkedIn
- category
- evidence ledger
- signal counts
- score snapshots

这是整个系统的中心，而不是聊天界面。

### Layer 5: Evidence-Backed Scoring

先定义可解释的 scoring rubric，再根据 evidence 打分。

推荐维度：

- Team
- Market
- Business
- Tech
- Momentum

关键原则：

- 分数必须可回溯到证据
- 相同来源重复报道要衰减
- 高可信来源权重大于社交噪音
- 缺失信息记为 unknown，不强行补全

### Layer 6: Output And Decision Support

最终输出不只是 summary，而是投资可执行信息：

- Top candidates
- Why now
- Score breakdown
- Key evidence
- Unknowns / risks
- Suggested follow-up questions

## 6. What Should Be Emphasized In Discussion

如果这份题目是用来做面试交流，当前最建议强调的点是：

1. 这不是一个 chatbot，而是一个 continuous sourcing pipeline
2. 第一步不是抓取，而是定义目标池
3. 最难的部分不是搜索，而是 entity resolution
4. LLM 负责结构化理解，不直接拍板投资价值
5. 排序必须 evidence-backed and explainable
6. 输出是 priority list，不是普通日报

## 7. What A Reasonable Interview Submission Looks Like

基于题目“主要体现思路”的要求，一个合理的交付不必是完整产品。

更实际的交付包应是：

- 一份方案文档
- 一张系统架构图
- 一个小型 GitHub demo
- 一份样例输出

这个 demo 只要能证明下面这条链路成立，就已经足够说明问题：

> source signals -> structured extraction -> company profile -> scoring -> ranking brief

## 8. Current Recommended Positioning

当前最推荐的定位表述是：

> 这不是一个新闻摘要工具，而是一个持续运行的 deal sourcing and ranking system。系统持续扫描多源信息，识别和 Agent 安全相关的公司，将分散证据归并到统一公司画像，再通过团队、市场、业务、技术和动量等维度做可解释评分，最后只把最值得投资人优先查看的机会输出成 brief。

## 9. Open Questions

如果后续要继续细化，这几个问题还需要继续明确：

1. Core vs Adjacent 的 taxonomy 是否要更细
2. company profile 的字段边界如何定义
3. scoring rubric 的每一项证据如何映射到分值
4. 哪些来源属于高可信源，权重如何设置
5. push 逻辑是 daily brief 还是 event-driven alert

