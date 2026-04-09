# Agent Security Radar

## Overview

Agent Security Radar 不是一个“帮我搜资料的 Agent demo”，而是一套给风投团队用的 deal sourcing workflow。

它要解决的问题很直接：

- 市场上和 Agent Security 相关的信息很多，但非常分散
- 新公司往往先出现在社交媒体、招聘页、技术博客、GitHub，而不是标准数据库里
- 很多名字看起来相关，但并不真的属于 Agent Security 投资范围
- 投资团队最缺的不是内容，而是 `先看谁` 的优先级

所以这个项目的目标不是做一份 summary，而是：

> 持续发现值得关注的 Agent Security 公司，把多源信号整理成公司画像，再输出一份投资人可以直接使用的 shortlist。

## Why Now

Agent 安全正在从“泛 AI 安全的一部分”变成更独立的问题域。

因为 agent 不只是回答问题，它会：

- 调工具
- 拿权限
- 访问企业数据
- 调用外部系统
- 自动执行动作

这就带来了新的安全需求，比如：

- runtime control
- policy guardrails
- prompt / tool injection defense
- agent identity and access control
- observability and audit
- sandboxing

对 VC 来说，这意味着新的公司会比“共识形成”更早出现。  
如果还靠人工零散刷推特、刷新闻、看数据库，通常会错过早期发现窗口。

## What This Project Is

这套东西应该被理解成一个 `continuous sourcing system`，而不是一个聊天机器人。

它的职责是：

1. 定义什么公司属于 Agent Security 投资范围
2. 持续从多种来源收集线索
3. 把零散信息归并成公司画像
4. 基于证据做优先级排序
5. 给投资团队输出“为什么现在值得看”和“下一步该问什么”

一句话说：

> 它不是帮投资人多看信息，而是帮投资人更快决定下一步该看哪家公司。

## Universe Definition

这件事最重要的第一步，是先定义目标池。

如果不先定义清楚什么叫 `Agent Security company`，后面抓再多数据都没有意义。

这里最关键的边界是：

> `using AI for security` 和 `securing AI agents` 不是一回事。

所以建议把目标池分成三层：

### Core

直接属于主扫描池、应该进入主 ranking 的公司：

- agent runtime security
- tool permissioning
- prompt injection defense
- agent identity and access control
- policy guardrails
- agent observability and audit
- agent sandboxing

### Adjacent

相关，但不一定直接进入主榜单的公司：

- broader AI security
- model governance / risk
- AI data leakage prevention
- AI supply chain security
- 没有明显 agent 场景的 LLM firewall

### Out of Scope

不应该进入主投资范围的对象：

- 传统安全公司，只是用了 AI 包装
- 没有安全产品的 AI 应用公司
- 通用 agent builder
- 纯研究项目

## Workflow

如果用业务流程的方式讲，这个系统分成 5 步：

### 1. Continuous Discovery

系统持续从不同来源收集线索，例如：

- X / Twitter
- LinkedIn
- GitHub
- 官网与产品文档
- 新闻和媒体
- PitchBook / The Information
- 论文

这里先解决“发现”问题，不急着做复杂判断。

### 2. Relevance And Universe Check

收进来的线索先判断：

- 它是不是和 Agent Security 有关
- 属于 Core、Adjacent，还是 Out of Scope
- 是否值得进入后续整理流程

这一步的目的，是避免目标池被泛 AI security 或噪音内容污染。

### 3. Company Profiling

这是整套系统最核心的部分。

一家公司可能同时出现在不同来源里，系统要把这些信号合成一个 company profile，而不是让分析师自己拼。

每个 profile 至少应该包含：

- company name
- aliases
- category
- recent signals
- evidence sources
- score breakdown
- unknowns
- follow-up questions

这一步真正解决的是“整理问题”，而不只是“搜索问题”。

### 4. Evidence-Backed Ranking

系统再按几个容易理解的维度做排序：

- Team
- Market
- Business
- Tech
- Momentum

重点不是分数多精准，而是分数必须说得清楚。  
也就是说，为什么这家公司排在前面，必须能回到具体证据。

### 5. Analyst Handoff

最终输出给投资团队的，不是普通日报，而是可以直接进入下一步讨论的 shortlist。

每个候选卡片应该回答：

- 这家公司做什么
- 为什么属于这个赛道
- 为什么现在值得关注
- 证据来自哪里
- 还缺什么信息
- 下一步人工该问什么

## What The Output Looks Like

最终输出应该更像一份投资团队会看的 candidate pack，而不是工程日志。

建议至少包含：

- `Top Candidates`
  这周或今天最值得优先看的公司
- `New Entrants`
  新进入 radar 的名字
- `Meaningful Changes`
  已跟踪公司出现的重要变化
- `Company Cards`
  why now / evidence / unknowns / follow-up questions

## How 7x24 Works

这里不要讲成“写个 while true 无限循环”。

更靠谱的讲法是：

> 7x24 的意思不是脚本永远不退出，而是整套流程持续在线、按节奏更新、出问题时能被及时发现。

一个更像真实系统的实现方式是：

- 高时效来源每 15 分钟扫描一次
- 常规来源每小时扫描一次
- 每天重算一次 ranking
- 每周生成一次更完整的 review

### Heartbeat Is For Reliability, Not Analysis

heartbeat 可以提，但要讲准。

它的作用不是帮你分析公司，而是帮你知道系统有没有正常工作：

- 某个 worker 还活着吗
- 某个来源是不是卡住了
- 今天的 radar 有没有正常产出

所以 heartbeat 更像运维层的健康信号，不是投研层的业务逻辑。

更完整一点可以说成：

- scheduler 负责发任务
- queue 负责排队
- workers 负责抓取、抽取、归并、打分
- database 存 company profile 和 evidence
- monitor 负责 heartbeat、health checks 和 alerts

## What The MVP Actually Proves

这次面试不需要交一个生产级系统。  
更合理的 MVP 是证明 workflow 是成立的。

MVP 需要证明：

- 多源信号可以被统一表示
- 不同来源的别名可以归并成一个公司画像
- 公司可以先被放进正确的 universe tier
- 排序结果可以被翻译成 investor-friendly candidate cards

也就是说，代码不是主角。  
代码只是证明这套业务流程是可以被自动化执行的。

## What Makes This A Strong Interview Answer

这套说法比“我做了一个 Agent demo”更强，是因为它主语是对的。

它的主语不是：

- 模型
- 抓取技术
- Agent 框架

而是：

- VC 团队的 sourcing 问题
- 投资范围的定义
- 证据归并和优先级排序
- 分析师下一步怎么行动

所以如果最后只留一句对外表达，可以用这个版本：

> This project is not positioned as a generic information-scraping agent. It is designed as a deal sourcing workflow for a VC team: first defining the investment universe for Agent Security, then continuously discovering and aggregating company signals, ranking candidates based on evidence-backed criteria, and finally outputting an investment-ready shortlist with why-now context and follow-up questions.
