# Agent Security Radar Proposal

## Goal

设计一个 7x24 小时运行的 scouting agent，持续扫描公开与半结构化信息，发现值得投资的 Agent 安全公司，并输出可解释的优先级排序。

## What The Agent Must Do

1. 从多源信息中召回候选公司
2. 把分散信号归并成统一的公司画像
3. 用可解释 rubric 评分，而不是让大模型直接决定值不值得投
4. 把结果整理成投资人可消费的 brief

## Source Layers

- `Discovery sources`: X, Reddit, LinkedIn, news,公众号, papers
- `Validation sources`: official site, GitHub, docs, hiring pages, funding databases
- `Deep dive sources`: founder history, product docs, code repos, research, partner/customer mentions

## Core Design Choice

真正难点不是“抓信息”，而是 `entity resolution + evidence-backed ranking`。

因此系统中心不是聊天框，而是一个 `Company Profile Layer`：

- 一个公司档案下面挂所有证据
- 分数来自证据累计
- 每一项结论都能追溯到 source 和 timestamp

## Demo Boundary

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

## How To Explain It In The Interview

可以用这句当主轴：

> I would build this as a continuous sourcing pipeline, not as a chatbot. The system first collects and normalizes signals, merges them into company profiles, then ranks companies with an evidence-backed rubric, and only after that generates a brief for investors.
