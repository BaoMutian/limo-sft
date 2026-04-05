# MathArena 基准说明

最后核对日期：2026-04-05

## 它是什么

`MathArena` 不是单一数据文件，而是一整套面向新鲜数学竞赛题的 benchmark 家族。  
它的核心思路是：持续引入新近发布的竞赛、奥数、研究型或图像题，以降低训练数据污染带来的记忆优势。

所以从产品形态上看，`MathArena` 更接近：

- benchmark suite
- leaderboard / evaluation platform
- 多任务家族

而不是一个像 `MATH-500` 那样的单文件静态 benchmark。

## 它主要测什么

本地副本能看出 `MathArena` 同时覆盖了三类能力：

- **文本 exact-answer 数学题**
- **图像驱动的 exact-answer 题**
- **proof / partial-credit 题**

这比传统只看最终 boxed answer 的 benchmark 更宽，尤其适合看：

- 新鲜竞赛题适应能力
- 图像题表现
- 证明题与部分分能力

## 本地离线副本

以下统计来自本地目录 [`MathArena`](/Users/sky/Datasets/MathArena)：

- 子集目录：**24**
- 总题数：**648**
- 其中文本 exact-answer：**439**
- 图像 exact-answer：**168**
- proof / partial-credit：**41**
- 带 `sample_solution` 的 proof 题：**15**

本地包含的子集有：

- `AIME`
- `HMMT`
- `Kangaroo`
- `USAMO`
- `IMO`
- `IMC`
- `CMIMC`
- `SMT`
- `ArXivMath`
- `Brumo`
- `Miklos`

每个子集单独存成 parquet 文件，因此结构并不统一：

- 一些子集只有 `problem` + `answer`
- 一些 proof 子集有 `points`、`grading_scheme`
- 一些图像子集带 `image` 字段而没有可直接显示的文本题面

## 它是怎么评测的

`MathArena` 的关键不只是答案对不对，而是 **按题型切不同评测方式**：

- 对 exact-answer 题，通常看最终答案是否正确
- 对图像题，还要求模型能处理图像输入
- 对 proof 题，则需要 grading rubric 或 judge 参与，不能退化成简单 exact match

这也是它和 `MATH-500`、`GPQA` 的最大差异：`MathArena` 从一开始就不是单一评分机制。

## 为什么本地查看器只能展示“结构化摘要”

当前本地数据里，`Kangaroo` 这类图像题把主要题面放在 `image` 字段里，而不是普通文本列。  
为了避免把大体积二进制图片直接塞进浏览器数据文件，这次页面查看器只保留：

- subset 名称
- 题号
- 是否图像题 / 是否 proof 题
- 文本题面（若有）
- 标准答案（若本地副本已有）
- `sample_solution` / `sample_grading` 预览（若有）

也就是说，这个查看器适合快速理解 benchmark 家族结构，但不等于完整重建官方站点体验。

## 重要 caveat

- `MathArena` 是滚动更新体系，本地副本只是某个时间点的快照
- 子集结构不统一，不能用一个统一 scorer 描述全部任务
- 图像题的题面在本地 parquet 中以图片字段存放，因此轻量查看器不会直接内嵌原图
- proof 题评分依赖 rubric / judge，不能简单套 exact match

## 当前结论

一句话总结：

`MathArena` 是一个以“新鲜数学题 + 多评测形态”为核心的 benchmark 家族，明显比静态单文件 benchmark 更接近真实前沿数学评测平台。

## 参考

- 官方站点：<https://matharena.ai/>
- 官方仓库：<https://github.com/MathArena/matharena>
- 本地目录：[MathArena](/Users/sky/Datasets/MathArena)
