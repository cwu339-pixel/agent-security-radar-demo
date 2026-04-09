# 目标池定义备忘录

## 定义

`Agent 安全公司` 指的是那些产品直接解决 AI agent 在自主调用工具、访问数据、执行动作、与外部系统交互时产生的新型安全、控制、治理、审计或隔离问题的公司。

重点是：

- 保护 agent
- 控制 agent 行为
- 管理 agent 权限
- 防止 prompt / tool 注入
- 对 agent 行为做监控和审计

而不是：

- 用 AI 做安全
- 泛 AI 安全
- 传统安全产品换了 AI 包装

## 目标池分层

### Core

进入主 ranking 的公司：

- agent runtime security
- tool permissioning
- prompt injection defense
- agent identity and access control
- policy guardrails
- agent observability and audit
- agent sandboxing

### Adjacent

相关但不一定直接进入主榜单，建议进入 watchlist：

- broader AI security
- model governance / risk
- AI data leakage prevention
- AI supply chain security
- 没有明显 agent 场景的 LLM firewall

### Out of Scope

应主动排除：

- 传统安全公司，仅用 AI 做营销
- 没有安全 wedge 的 AI 应用公司
- 通用 agent builder
- 纯研究项目

## 最关键的一句话

`using AI for security` 和 `securing AI agents` 是两回事。  
在任何抓取和排序开始之前，必须先把这个边界定义清楚。
