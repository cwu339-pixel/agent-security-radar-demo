# 面试口述提纲

## 2-3 分钟版本

这题如果站在风投公司的角度看，核心不是做一个会搜信息的 Agent，而是设计一套 deal sourcing workflow。  
我会先定义什么公司属于 Agent Security 的投资范围，因为如果目标池没有定义清楚，后面抓取和排序都会漂。这里我会先把公司分成 core、adjacent 和 out-of-scope 三层。

然后系统层面我不会把它做成 chatbot，而是做成一条持续运行的 sourcing pipeline。第一层负责从 X、LinkedIn、GitHub、新闻和官网等来源收集代表性信号；第二层判断这些信号是否属于 Agent Security 的目标池；第三层把不同来源对同一家公司提到的内容归并成一个 company profile，这是系统里最关键的一层；第四层基于 team、market、business、tech、momentum 做 evidence-backed scoring；最后只把最值得优先看的公司输出成带有 why now、key evidence、unknowns 和 follow-up questions 的 candidate cards。

所以这个项目的价值不是自动替代投资判断，而是帮助 VC 团队更早发现机会、更系统地聚合证据，并且更快决定下一步先研究谁。

## 追问时可补的三句话

### 为什么不是普通日报

因为日报解决的是阅读问题，但 VC 更需要优先级问题。这个系统最终输出的应该是 short list，而不是 summary。

### 为什么要先定义 universe

因为 `using AI for security` 和 `securing AI agents` 是两回事。边界不清楚，系统就会把很多不该看的公司混进来。

### 为什么 MVP 足够

因为这次面试看的是 workflow 和思路。我用最小代码证明了 source signal -> company profile -> scoring -> investment brief 这条链是可以系统化执行的。
