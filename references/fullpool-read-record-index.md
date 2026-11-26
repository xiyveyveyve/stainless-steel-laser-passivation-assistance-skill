---
title: "不锈钢激光钝化 · 全池精读记录索引（1213 篇）"
type: index
status: verified
created: 2026-10-14
tags:
  - 科研系统
  - 文献证据
  - 不锈钢激光钝化
  - 索引
---

> **source_registration: none（索引产物）** —— 本索引指向逐篇精读记录，**未登记**入 `source-map.csv`。

# 全池精读记录索引

## 0. 这是什么

全池逐篇精读（P0–P4）产出 **1213 份**逐篇记录（`_readscreen_[A-Z]+.json`），每份含 30–60 条 `key_values`（原文照抄 + 单位 + 页码锚点）。

原始记录位置：

```
D:/杂物间/不锈钢激光钝化skill相关数据/candidate-pool-2026-09-27/_readscreen_[A-Z]+.json
```

## 1. 索引表

`fullpool-read-record-index.csv` —— 1213 行，列为：

| 列 | 含义 |
|---|---|
| `paper_id` | 文献标识（DOI 或 `OA_/SPR_/WILEY_` 前缀形式）|
| `has_target_data` | 是否含本 skill 目标数据（true/false）|
| `mismatch_type` | 误捞类型（a/a′/b/c/d/e/f/h/j/k/m/o 或空）|
| `material` | 材料 |
| `laser_process_short` | 激光工艺（截断 200 字）|
| `mechanism_short` | 机制（截断 200 字）|
| `key_values_count` | 抽取的量化条目数 |

## 2. 覆盖统计

| 项 | 数值 |
|---|---|
| 精读文献（去重）| **1213 篇** |
| key_values | **45498** |
| has_target_data | **true 314 / false 899（25.9%）** |
| 分阶段 | P0 83 · P1 191 · P2 201 · P3 618 · P4（L7）75 |

**约 74% 是误捞** —— 「不锈钢 + 激光 + 腐蚀」的字面组合远多于真正的「激光钝化」。

## 3. 如何检索

```powershell
# 找所有含激光表面处理的命中文献
Import-Csv fullpool-read-record-index.csv | Where-Object { $_.has_target_data -eq 'true' } | Select-Object paper_id, laser_process_short

# 找特定误捞类型
Import-Csv fullpool-read-record-index.csv | Where-Object { $_.mismatch_type -like '*a*' }
```

或直接读取对应的 `_readscreen_*.json` 取完整 `key_values`。

## 4. 相关分析产物

| 文件 | 内容 |
|---|---|
| `laser-passivation-knowledge-synthesis.md` §8 | 全池核心发现汇总 |
| `laser-passivation-negative-thresholds.md` | **负面阈值与决定性反例**（必读）|
| `laser-plus-electrochem-p4-addendum.md` | L7 批次（激光∧XPS）补充证据 |
| `laser-plus-electrochem-table.csv` | 激光+电化学同篇证据表（37 行）|
| `L3-mott-schottky-table.csv` | Mott-Schottky 参数表（167 行）|
| `L456-DLEPR-table.csv` | DL-EPR/DOS 参数表（262 行）|
