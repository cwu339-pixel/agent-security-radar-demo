# Agent Security Radar

一个面向风投团队的持续投研流程原型，用来扫描 Agent Security 领域并输出投资人可直接阅读的候选公司 shortlist。

## 这个项目做什么

```text
信号输入 → 相关性分类 → 公司画像 → 打分排序 → 投资 shortlist
```

系统会：

1. 从 GitHub、X/Twitter、Reddit、Hacker News 收集信号
2. 判断每条信号是否属于 Agent Security 目标池
3. 把多源信号归并成统一公司画像
4. 按团队、市场、业务、技术、动量五个维度打分
5. 输出带有证据、未知项和后续追问的候选公司卡片

## 快速开始

### Demo 模式

不需要 API key，直接用代表性样本数据跑完整流程：

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m agent_security_radar.cli demo
```

### 实时扫描模式

需要 OpenAI API key，会从真实来源抓取内容并做 LLM 分类：

```bash
cp .env.example .env
# 在 .env 里填写 OPENAI_API_KEY

PYTHONPATH=src python -m agent_security_radar.cli scan
PYTHONPATH=src python -m agent_security_radar.cli scan --sources github hackernews
PYTHONPATH=src python -m agent_security_radar.cli scan --max 10
```

### 运行测试

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## 输出结果

- `outputs/ranking.json`：结构化公司数据，包含打分和证据
- `outputs/daily_brief.md`：面向投资人的 Markdown 简报

## 输出示例

```md
### 1. Noma Security (75)
- 目标池分层：核心目标池
- 赛道类别：Agent 运行时安全

评分拆解：
- team: 8 | market: 19 | business: 15 | tech: 20 | momentum: 13

为什么现在值得看：
- 明确围绕 agent security 使用场景展开。

目前还不知道什么：
- 创始人与核心团队的履历还需要进一步确认。

建议下一步追问：
- 创始人是否有连续创业或安全 / AI infra 背景？
```

## 架构

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   抓取层     │────>│   分类层      │────>│   公司画像层      │
│              │     │  (LLM/规则)   │     │                  │
│ · GitHub     │     │              │     └────────┬─────────┘
│ · X/Twitter  │     │ · 相关性      │              │
│ · Reddit     │     │ · 目标池分类  │     ┌────────▼─────────┐
│ · HackerNews │     │ · 标签抽取    │     │    打分引擎       │
└──────────────┘     └──────────────┘     └────────┬─────────┘
                                                   │
                                          ┌────────▼─────────┐
                                          │   shortlist 输出  │
                                          │  (投资人可读)     │
                                          └──────────────────┘
```

## 目标池定义

| 分层 | 含义 | 举例 |
|------|------|------|
| **核心目标池** | 直接做 Agent Security 产品的公司 | runtime guardrails、agent auth、sandbox、注入防护 |
| **相邻观察池** | 相关但不是纯 Agent Security | 通用 AI security、model scanning、LLM firewall |
| **不在目标范围内** | 没有 Agent Security 角度 | 传统安全公司、无安全方向的 agent builder |

## 打分维度

| 维度 | 看什么 |
|------|------|
| **团队** | 创始人背景、安全经验、关键招聘 |
| **市场** | 是否真正聚焦 Agent Security、时机是否成立 |
| **业务** | 客户、融资、GTM 信号 |
| **技术** | GitHub 活跃度、技术深度、开源情况 |
| **动量** | 最近更新、媒体曝光、招聘和增长信号 |

每个分数都必须能回到具体证据，没有证据就不加分。

## 项目结构

```text
├── src/agent_security_radar/
│   ├── pipeline.py          # 打分、归并、排序核心逻辑
│   ├── render.py            # 简报输出
│   ├── cli.py               # CLI 入口（demo + scan）
│   ├── scrapers/            # 4 个来源的抓取器
│   ├── analyzer/            # LLM 分类器 + 事件去重
│   └── models/              # ContentItem 数据模型
├── data/sample_signals.json # 代表性样本数据
├── outputs/                 # 生成的简报和排名
├── tests/                   # 单元测试
└── docs/                    # 设计文档
```

## 设计说明

完整设计思路见 [docs/direct-share-summary.md](docs/direct-share-summary.md)。
