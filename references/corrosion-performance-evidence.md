---
title: "Corrosion and electrochemistry — domain reference"
type: skill-domain-reference
skill: stainless-steel-laser-passivation
reference_id: corrosion_electrochemistry
date: 2026-08-14
status: release
source_index:
  - "s5-performance-source-anchors.csv"
  - "evidence-index.jsonl"
---

# Corrosion and electrochemistry — domain reference

> 用途：把腐蚀和电化学作为钝化有效性与稳定性证据，而不是让腐蚀指标
> 单独决定膜层机制。每条数值都必须保留打包索引中的来源状态和锚点。

## 1. 电化学方法证据边界

| 技术 | 必须记录字段 | 可比性规则 | 关键锚点 |
|---|---|---|---|
| OCP/腐蚀电位 | 参比电极、温度、稳定时间 | 电位注明参比+温度；跨参比按 ASTM G220 / Pine 换算 | ISO 17474; ASTM G220 |
| 动电位极化 (PDP) | 扫描速率、起止电位、面积、除氧、iR | 扫描速率影响显著（0.1667~1 mV/s 常用，快扫失真）；Tafel 区域影响 icorr 数量级 | ISO 17475; ASTM G5/G59; SCANRATE-AL-2021 |
| 循环极化 (CPP) | 反向判据、反向电流阈值、滞后环 | Epit/Eprot 与滞后环解读需固定反向电流判据 | ASTM G61; Metrohm AN-COR-016; RSM-316-2024 |
| 极化电阻 (LPR/Rp) | B 值、线性窗口、iR 补偿、频率 | Stern-Geary 仅 ±10~20 mV 近似线性；扩散控制时 LPR 低估可达数量级 | ASTM G59; LPR-IR-2014; MATTHEWS-1975 |
| EIS | 频率范围、振幅、线性/平稳性验证、拟合模型 | KK/Lin-KK 验证因果性；非平稳需 Z-HIT；CPE/电路非唯一 | ISO/TR 16208; ISO 16773; EIS-NONLINEAR-2023; CPE-EQUIV-2021 |
| Mott-Schottky | 频率、电位扫描方向、缺陷类型假设 | 单一频率 M-S 解读需谨慎；接触注入电容可冒充耗尽电容 | MOTT-RAVISHANKAR-2022; 654SMO-C276-2024 |
| 电化学噪声 (EN) | 采样率、趋势去除、LI | Rn 与 icorr 换算、腐蚀类型（LI 判据） | EN-304NG-2014; 15-5-17-4PH-PASS-2020 |

来源追溯：方法条目通过打包的 `s5-performance-source-anchors.csv` 和
`evidence-index.jsonl` 关联到 `source_id` 与页/表/图锚点；未关联的条目标记为
`needs_user_review` 或 `source_unavailable`。

## 2. 单位与换算

- 电位：V vs SCE / Ag/AgCl / SHE 必须互换算；Ag/AgCl(3M KCl) 与 SCE 差约 −45 mV（随温度变）；
- 电流密度：µA/cm² 与 mA/cm² 混用需统一；面积必须记录；
- 阻抗：Ω·cm²（面积归一）与 Ω 区分；CPE 单位 Ω⁻¹·cm⁻²·sⁿ；
- 腐蚀速率：mm/year 由 icorr 按 ASTM G102 换算（当量重量/密度/电子数）。

## 3. 数值证据引用规则

- 每条数值保留原单位、参比电极、面积、协议、n/error、页/表/图锚点；
- `reported` = 表格/正文转写核对；`figure_only` = 仅曲线无数值，不承担回归验证；
- 例示数值（如 654SMO、316L-SENS、NASS/304 CPP、LPBF 316L、PH 钝化对照和
  PDM/RSM 结果）只能按其对应的 `source_id`、材料、协议和证据状态使用；逐条
  锚点见打包的 `s5-performance-source-anchors.csv` 与 `evidence-index.jsonl`。

## 4. 失败与反例（不挑选较好结果）

- EIS 非线性/不平稳（EIS-NONLINEAR-2023）；漂移校正（EIS-DRIFT-2023）；Z-HIT（ZHIT-REVIEW-2021）；
- KK 验证（ASTM KK 1993 / KK-ZINC 2007 线索）；
- CPE 非唯一（CPE-EQUIV-2021）；ECM 贝叶斯模型选择（ECM-BAYES-2024/npj）；
- Stern-Geary 线性窗口（MATTHEWS-1975）；iR 补偿（LPR-IR-2014）；低腐蚀速率 LPR 频率偏差（SKB）；
- 扫描速率效应（SCANRATE-AL-2021）；参比电极漂移（REF-AGAGCL-2024）；宏电池极化不均匀；
- M-S 批判（La Mantia 2010、Ravishankar 2022）；
- 同一样品不同拟合方案冲突：马氏体 PDM 双模型、EEC-AM-316L-2020（需 XPS 佐证）、EEC-COMPARE-2006。

来源追溯：失败和反例条目必须在 `s5-performance-source-anchors.csv` 或
`evidence-index.jsonl` 中找到对应锚点；没有锚点时仅作为待核验提示。

## 5. 矛盾处理

- XPS 与电化学冲突：保留双方，不挑较好结果；
- 不同钢种/电解液/协议混用：禁止未经说明横向排序；
- 性能指标只能支持其实际测量范围内的结论；缺 n/面积/参比/拟合质量 → 显式降级。

## 打包资源与追溯

- `s5-performance-source-anchors.csv`：电化学性能与失败案例锚点。
- `evidence-index.jsonl`：逐条观察、状态和置信度索引。
- `source-map.csv`：来源元数据、可访问性和文件校验信息。

## 边界规则

- Treat corrosion/electrochemistry as supporting evidence for passivation, not as a standalone mechanism claim.
- Keep reference electrode, temperature, area, scan rate, iR compensation, repeat count, fit quality, and exposure protocol attached to every comparison.
- Preserve `reported`, `figure_only`, `author_interpretation`, `derived`, `blocked`, and `deferred` states; do not rank unlike protocols as if they were equivalent.
- Mott-Schottky, EIS equivalent circuits, and single-point corrosion improvements cannot establish a unique film mechanism without independent chemical/structural evidence.
