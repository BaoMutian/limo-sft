# MATH-500 基准说明

最后核对日期：2026-04-05

## 它是什么

`MATH-500` 是一个固定的 500 题数学推理评测集。它不是动态 leaderboard，也不是线上提交平台，而是一个 **离线 final-answer 数学 benchmark**。

OpenAI 在 PRM800K / “Let’s Verify Step by Step” 相关材料里说明过它的来历：他们从原始 `MATH` 数据里做了一个非标准拆分，把大部分训练题和测试题重新用作训练，只留下 500 道真正 hold-out 的测试题作为 `MATH-500`。

## 它主要测什么

`MATH-500` 测的是：

- 文本条件下的数学推理
- 最终答案正确性
- 代数、几何、数论等经典竞赛数学能力

它不测：

- 工具调用
- 网页检索
- 多模态文件理解
- proof judge 打分

从评测形态看，它属于 **静态、文本、离线 final-answer benchmark**。

## 本地数据结构

以下统计来自本地目录 [`MATH-500`](/Users/sky/Datasets/MATH-500)：

- 文件：`README.md`、`eval.yaml`、`test.jsonl`
- 题数：**500**
- 字段：`problem`、`solution`、`answer`、`subject`、`level`、`unique_id`

本地派生统计：

- 学科分布：Algebra 124，Intermediate Algebra 97，Prealgebra 82，Number Theory 62，Precalculus 56，Geometry 41，Counting & Probability 38
- 难度分布：level 1 = 43，level 2 = 90，level 3 = 105，level 4 = 128，level 5 = 134
- 题面平均长度约 195.9 字符，中位数约 148
- 解答平均长度约 531.3 字符，中位数约 421.5
- 本地答案形式大致分为：数值 318，LaTeX 表达式 135，列表 28，文本 11，等式 4，区间/有序对 4

因为 `test.jsonl` 里已经直接给出 `solution` 和 `answer`，所以当前本地副本不是 hidden-label 包。

## 它是怎么评测的

本地 [`eval.yaml`](/Users/sky/Datasets/MATH-500/eval.yaml) 当前把它包装成 inspect-ai 任务，关键点包括：

- split：`test`
- `epochs: 4`
- `epoch_reducer: pass_at_1`
- 输入字段：`problem`
- 目标字段：`answer`
- prompt 模板要求模型最后输出 `Therefore, the final answer is: $\boxed{ANSWER}$. I hope it is correct`
- scorer：`model_graded_fact`

所以它虽然是数学 benchmark，但当前本地配置并不是纯字符串 exact match，而是通过 `model_graded_fact` 去比较最终答案。

## 这个 benchmark 该怎么用

比较合理的使用方式是：

1. 作为离线数学推理回归集
2. 跟踪不同 prompt / sampling / verifier 配置的稳定性
3. 结合 `subject` 和 `level` 分桶看模型短板

不太适合把它当成“线上最新榜单”来理解，因为它本质上是静态 hold-out 集。

## 重要 caveat

- 本地副本已含答案与完整解答，不是公开 test-only hidden labels
- 复现时要注意你使用的是当前 `eval.yaml` 的 judge 方式，还是更严格的 rule-based / exact-answer 方式
- `MATH-500` 的价值主要在稳定、可复现，不在“新鲜度”

## 当前结论

一句话总结：

`MATH-500` 是一个非常适合离线回归的静态数学 final-answer benchmark，但它不是 agent benchmark，也不是实时榜单平台。

## 参考

- OpenAI PRM800K 仓库：<https://github.com/openai/prm800k>
- 本地目录：[MATH-500](/Users/sky/Datasets/MATH-500)
