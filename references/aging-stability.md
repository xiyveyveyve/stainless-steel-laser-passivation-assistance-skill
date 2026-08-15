---
title: "Aging and stability — domain reference"
type: skill-domain-reference
skill: stainless-steel-laser-passivation
reference_id: aging_stability
date: 2026-08-14
status: release
source_index:
  - "s5-performance-source-anchors.csv"
  - "evidence-index.jsonl"
---

# Aging and stability — domain reference

> 用途：分类浸泡、盐雾、长期暴露、膜层退化和恢复的证据。
> 短期有效不能外推长期稳定；任何矛盾结果保留，不通过"挑选较好结果"消除。
> 若请求同时包含长期稳定性与 XPS 终点（即使只有一个时点），必须并集加载
> `surface-chemistry-xps.md` 与 `xps-record.schema.yaml`；涉及膜机理或电化学时再按问题加载
> `passive-film-formation.md` 或 `corrosion-performance-evidence.md`。

## 1. 暴露类型与证据要求

| 暴露类型 | 必须记录 | 证据分级 |
|---|---|---|
| 短期浸泡（<24h） | 溶液/温度/时间/面积/协议 | 仅支持短期行为，不外推长期 |
| 长期浸泡（天~月） | 暴露时长、定期取样、膜化学/性能跟踪 | 可支持长期稳定性结论 |
| 盐雾（ASTM B117 等） | 盐雾浓度/温度/时长/判据 | 加速试验，非现场等效 |
| 干湿/热循环 | 循环次数/周期/温度范围 | 支持耐久性边界 |
| 现场暴露（海洋大气等） | 地点/季节/暴露时长 | 最接近服役，但变量不可控 |

## 2. 时效与膜退化证据边界

| 现象 | 直接证据 | 不可判定时 |
|---|---|---|
| 膜层退化 | 暴露后膜化学（XPS）或电化学指标恶化 + 时间依赖 | 单点恶化不能证明退化动力学 |
| 膜层恢复 | 暴露后指标回升（再钝化） | 回升可能是测量波动 |
| 短期有效—长期衰退 | 多时间点数据明确转折 | 无长期数据不得宣称"长期有效" |
| 表面污染/吸附 | 化学分析+时间历史 | 污染 ≠ 膜退化 |

## 3. 反例与边界（负结果集）

- 激光织构长期润湿性演化（Conradi 2019：即时/3个月/1年变化）；
- 超亲水→超疏水转变（CorrSci 2017；LiM2019 14 天亲水→疏水）；
- 激光标记短期点蚀电位下降、长期接近未标记基材（Zhang 2020）；
- 304L 激光标记长期 SCC/氯环境风险（CRIEPI 2012）；
- LSP 有无保护涂层方向相反（Chiang 2026）；
- 清洗移除激光再沉积颗粒改变结果归因（Dasaev 2023）；
- 纹理密度/自由表面能导致相反趋势（AhuirTorres 2025）；
- 热输入窗口反转（Kučera 2014）。

来源追溯：负结果条目必须通过打包的 `s5-performance-source-anchors.csv` 与
`evidence-index.jsonl` 解析到 `source_id` 和页/表/图锚点；未能解析的条目标记为
`source_unavailable`，不得作为已核验事实使用。

## 4. 判定规则

1. 报告暴露时长或循环次数 + 至少一种定量耐蚀指标；
2. 优先同钢种/同表面状态/未处理对照；
3. 只给"耐蚀性提高"而无条件/数值 → 降级为 mechanism/context；
4. 记录改善/恶化/无变化/短期有效-长期衰退四类结果。

## 打包资源与追溯

- `s5-performance-source-anchors.csv`：长期暴露与性能证据锚点。
- `evidence-index.jsonl`：逐条证据索引；使用前保留其状态和置信度。
- `source-map.csv`：来源元数据、可访问性和文件校验信息。

## 边界规则

- Do not extrapolate short exposure, salt spray, or wettability changes to service-life claims without duration-matched evidence.
- Preserve improvement, deterioration, no-change, and short-term/long-term reversal as separate outcomes.
- Keep laser marking, texturing, shock peening, coating, and thermal histories distinct; no cross-process ranking without a protocol match.
- Mark inaccessible or unreported long-term data as `source_unavailable`, `not_reported`, or `deferred`, never as a default stable result.
