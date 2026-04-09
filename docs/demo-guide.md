# 演示说明

## 面试时建议的展示顺序

如果时间很短，建议按这个顺序展示：

1. `docs/investment-universe.md`
2. `docs/workflow-design.md`
3. `outputs/daily_brief.md`
4. `src/agent_security_radar/` 里的最小代码

这样重点会落在投研 workflow，而不是代码细节。

## 运行方式

```bash
cd /Users/wuchenghan/interview_prep/agent-security-radar-demo
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/run_demo.py
```

## 这份 MVP 真正证明了什么

- 多源样本可以统一处理
- 公司别名可以归并
- 可以先做目标池分类，再做排序
- 最终输出可以长成投资人能消费的卡片

## 这份 MVP 没有证明什么

- 真实数据抓取得足够全
- 7x24 调度已经做好
- 真实环境下的 LLM 抽取准确率
- 生产级别的稳定性
