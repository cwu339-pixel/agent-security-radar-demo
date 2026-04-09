# Agent Security Radar 项目说明

## 目标

设计一个 7x24 小时运行的 scouting agent，持续扫描公开与半结构化信息，发现值得投资的 Agent 安全公司，并输出可解释的优先级排序。

## 这个系统要做什么

1. 从多源信息中召回候选公司
2. 把分散信号归并成统一的公司画像
3. 用可解释 rubric 评分，而不是让大模型直接决定值不值得投
4. 把结果整理成投资人可消费的 brief

## 信息源分层

- `发现层`：X、Reddit、LinkedIn、新闻、公众号、论文
- `验证层`：官网、GitHub、文档、招聘页、融资数据库
- `深挖层`：创始人背景、产品文档、代码仓库、研究、客户与合作伙伴信息

## 核心设计选择

真正难点不是“抓信息”，而是 `entity resolution + evidence-backed ranking`。

因此系统中心不是聊天框，而是一个 `Company Profile Layer`：

- 一个公司档案下面挂所有证据
- 分数来自证据累计
- 每一项结论都能追溯到 source 和 timestamp

## Demo 边界

为了把重点放在逻辑而不是工程量，这个 demo 只演示：

- 输入样本
- alias 归并
- 基于标签的评分
- 排名结果
- 投资 brief 输出

不包含：

- 实时爬虫
- 调度器
- LLM 信息抽取
- 外部数据库接入

## 面试里怎么讲

可以用这句当主轴：

> 我会把它做成一条持续运行的 sourcing pipeline，而不是 chatbot。系统先收集并标准化多源信号，再把这些信号归并到 company profile，之后用基于证据的规则完成排序，最后再生成投资人可直接阅读的 shortlist。
