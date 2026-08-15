---
title: "Measurement quality — domain reference"
type: skill-domain-reference
skill: stainless-steel-laser-passivation
reference_id: measurement_quality
status: release
date: 2026-08-14
source_index:
  - "s5-performance-source-anchors.csv"
  - "evidence-index.jsonl"
---

# Measurement quality — domain reference

> 用途：规定重复数、误差、随机化、拟合优度、异常值、单位和参比电位换算的
> 审查边界。证据不足时保留 `not_reported` 或 `needs_user_review`，不补默认值。

## 1. 统计与不确定度基础

| 主题 | 规则 | 依据 |
|---|---|---|
| 重复性/再现性 | 重复性标准差 sr 与再现性标准差 sR 分开；报告 n | ISO 5725-1:2023 预览 |
| 不确定度 | GUM 合成 u_c = sqrt(Σu_i²)，扩展 U = k·u_c | JCGM 100:2008 |
| 异常值 | 用稳健统计或明确排除规则；不静默丢弃 | ISO 5725-1; Coelho 2023 |
| 随机化/区组 | 区组中心点、随机顺序；报告设计 | Dastgerdi 2019 |
| 多重比较 | 少重复用 Bonferroni 校正而非 Tukey（Zweifach 2025）；双因素 ANOVA+Tukey（Ramos-Negrón 2026） | 相关证据的 `source_id` 与锚点 |
| 有效数字 | 误差与均值的有效位数一致 | 相关证据的 `source_id` 与锚点 |

## 2. 电化学测量质量

| 检查项 | 规则 | 依据 |
|---|---|---|
| 重复数 n | 每条数值必须报告 n；无 n 标 `not_reported` | `s5-performance-source-anchors.csv` + `evidence-index.jsonl` |
| 参比电极 | 类型+温度必须报告；跨参比换算按 G220 | 打包性能锚点与证据索引 |
| 工作面积 | 面积必须报告（如 0.785、4.46 cm²） | `s5-performance-source-anchors.csv` + `evidence-index.jsonl` |
| 拟合质量 | EIS 报告残差/χ²/置信区间；不唯一时显式声明 | EIS-NONLINEAR-2023; ECM-BAYES-2024 |
| 单位 | µA/cm² 与 mA/cm² 统一；Ω·cm² 面积归一 | 打包性能锚点与证据索引 |

## 3. 各仪器 SOP 锚点

| 仪器 | SOP/校准 | 依据（打包性能锚点与证据索引） |
|---|---|---|
| SEM | ISO 16700 放大率校准预览 | H-MEAS-ISO16700 |
| 轮廓仪 | ISO 25178-601/-700 校准验证预览 | H-MEAS |
| XPS | ISO 19318 荷电报告预览 | H-MEAS-ISO19318 |
| EIS | KK/Lin-KK 验证、Z-HIT | Metals 2020 KK |
| 接触角 | ISO 19403-2/-6 测量/SFE | H-MEAS-CA-SOP |

## 4. 反例（不把脚本成功当科学正确）

- XPS 定标失败（Greczynski 2022：盲信 C1s 校准风险）；
- 统计过度解读（Ioannidis 2005：多数研究发现为假）；
- 离群敏感性（Coelho 2023 稳健统计反例）；
- LPR 未补偿欧姆降/扩散 → 腐蚀速率低估数量级（LPR-IR-2014）；
- 低腐蚀速率 LPR 频率不匹配（SKB R-13-13）。

## 5. 禁止

- 缺 n/面积/参比/拟合质量仍作定量比较；
- 不同协议未说明直接横向排序；
- 只报 χ²/R² 证明模型唯一；
- 把单条测量当重复性。

## 打包资源与追溯

- `s5-performance-source-anchors.csv`：测量协议和性能数据锚点。
- `evidence-index.jsonl`：证据状态、置信度和锚点索引。
- `source-map.csv`：来源元数据、可访问性和文件校验信息。

## 边界规则

- Separate independent sample count from technical repeats and retain the reported error type (SD/SE/CI) and uncertainty basis.
- Require units, reference electrode and temperature, working area, iR treatment, protocol, and fit-quality metadata before quantitative comparison.
- Do not treat p-values, a lower chi-squared, or a single measurement as proof of practical significance, model uniqueness, or repeatability.
- If a standard is preview-only or a raw data file is unavailable, preserve that limitation in the evidence state.
