# GPQA / GPQA Diamond 基准说明

最后核对日期：2026-04-05

## 它是什么

`GPQA` 是一个面向生物、化学、物理三大领域的高难度研究生级选择题 benchmark。论文把它定位成“Google-proof” 科学问答集，意思不是完全无法检索，而是即使给非专家充分网页访问时间，单靠通用搜索也很难稳定答对。

实际使用里，大家最常报的是更小、更难的 `GPQA Diamond` 子集。

## 它主要测什么

`GPQA` 主要测的是：

- 高门槛学科知识
- 多选项干扰下的科学推理
- 在非开放生成任务中的最终答案选择能力

它不是 agent benchmark，也不测工具调用、文件处理或长链行动执行。  
更准确地说，它是一个 **高难科学多选推理 benchmark**。

## 本地数据结构

以下统计来自本地副本 [`GPQA`](/Users/sky/Datasets/GPQA)：

- `gpqa_diamond.csv`：198 题
- `gpqa_main.csv`：448 题
- `gpqa_extended.csv`：546 题
- `gpqa_experts.csv`：60 行专家元数据

各子集领域分布：

- `gpqa_diamond`：化学 93，物理 86，生物 19
- `gpqa_main`：化学 183，物理 187，生物 78
- `gpqa_extended`：化学 214，物理 227，生物 105

本地派生特征：

- `gpqa_diamond`：13 个 subdomain，35 位 question writer，平均题面长度约 431.3 字符
- `gpqa_main`：16 个 subdomain，47 位 question writer，平均题面长度约 446.5 字符
- `gpqa_extended`：16 个 subdomain，49 位 question writer，平均题面长度约 451.8 字符

这些 CSV 里不只包含最终题面和四个选项，还包含：

- 正确答案
- 错误选项
- explanation
- validator accuracy
- writer / subdomain 元数据

所以当前本地副本不是 hidden-label 测试包，而是 **完整公开内容副本**。

## 它是怎么评测的

本地 [`eval.yaml`](/Users/sky/Datasets/GPQA/eval.yaml) 采用的是 inspect-ai 风格多项选择评测：

- 输入字段：`Question`
- 选项字段：`Incorrect Answer 1`、`Incorrect Answer 2`、`Incorrect Answer 3`、`Correct Answer`
- 目标标签：字面上的 `D`
- `shuffle_choices: true`

这个设计很重要，因为：

1. 原始数据里正确答案列固定叫 `Correct Answer`
2. 真正评测时会先把四个选项打乱
3. 模型最终要选的是打乱后的正确选项，而不是记住“第四列永远是答案”

## 怎么理解 Diamond / Main / Extended

- `GPQA Diamond`：当前最常见的主报告子集，题数更少、难度更高
- `GPQA Main`：更大的标准多选集合
- `GPQA Extended`：更大的扩展集合
- `gpqa_experts.csv`：不是正式题目 split，而是专家/非专家表现元数据

如果你只是想和论文或近期模型报告对齐，优先看 `Diamond`。  
如果你想做更大规模离线评测，可以把 `Main` 和 `Extended` 一起纳入。

## 重要 caveat

- 这是 **公开题库**，不是线上隐藏标签榜单
- 本地 CSV 已经包含答案和解释，因此不能把它当成“未泄露测试集”
- 因为评测时会 shuffle choices，离线复现实验时必须复现这个过程
- `gpqa_experts.csv` 记录的是专家元数据，不应混进正式做题 split

## 当前结论

如果你的目标是评估模型在高门槛科学多选推理上的能力，`GPQA` 很有价值。  
如果你的目标是测 agent 系统能力，`GPQA` 就不是那类 benchmark。

一句话总结：

`GPQA` 是一个公开的高难科学多选 benchmark，而 `GPQA Diamond` 是其中最常用的硬子集。

## 参考

- 论文页：[GPQA: A Graduate-Level Google-Proof Q&A Benchmark](https://openreview.net/forum?id=Ti67584b98)
- Hugging Face 数据集：<https://huggingface.co/datasets/Idavidrein/gpqa>
- 本地数据目录：[GPQA](/Users/sky/Datasets/GPQA)
