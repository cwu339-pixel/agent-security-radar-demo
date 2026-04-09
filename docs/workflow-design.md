# 业务流程设计

## 设计原则

这套系统应该被理解成一条 `持续运行的投研 workflow`，而不是一个 chatbot。

它的主产品不是对话，而是一份基于证据的、面向投资人的公司优先级列表。

## 端到端流程

### 1. 信号采集

系统从这些来源收集代表性信号：

- X / Twitter
- LinkedIn
- GitHub
- 新闻
- 官网与产品文档
- 研究和数据库

所有信号统一成标准 schema，避免后续逻辑按来源分别处理。

### 2. 相关性与目标池分类

在排序之前，系统先判断这条信号是否属于目标投资范围。

这一层要回答：

- 它是不是和 Agent Security 有关
- 属于 `core`、`adjacent` 还是 `out_of_scope`
- 更具体属于哪一类

这样做的目的，是避免泛 AI security 或通用 agent 公司污染主榜单。

### 3. 公司画像层

这是整个 workflow 的中心。

不同来源可能会用不同名字提到同一家公司。系统会把这些信号合并成一个 company profile，其中至少包含：

- canonical name
- aliases
- category
- evidence ledger
- score breakdown
- unknowns

这一步把碎片化的市场噪音，变成投资人可以真正使用的对象。

### 4. 可解释打分

每个 company profile 按五个维度排序：

- Team
- Market
- Business
- Tech
- Momentum

打分的目的不是制造精确假象，而是强制系统回答：

> 为什么这个名字比另一个名字更值得优先关注？

### 5. 面向投资人的输出

最终输出是一份候选公司卡片 shortlist，包含：

- 目标池分层
- 赛道类别
- 分数拆解
- why now
- 关键证据
- unknowns
- follow-up questions

这能帮助投资人在有限时间里判断“接下来先花 20 分钟看谁”。

## 为什么这条 workflow 适合 VC

它和真实的投研动作是一致的：

- 定义目标池
- 发现候选公司
- 收集证据
- 横向比较
- 把最值得看的名字交给分析师继续跟

## 为什么这个 MVP 已经够了

真实生产系统当然还会加上实时抓取、调度、更多抽取能力。  
但面试里更重要的问题是：

> 这条投研 workflow 能不能被清楚定义、解释清楚，并且用最小原型证明它是可执行的？

这个 MVP 证明的就是这件事。
