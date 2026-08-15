---
title: "Passive film formation — domain reference"
type: skill-domain-reference
skill: stainless-steel-laser-passivation
reference_id: passive_film_formation
date: 2026-08-14
status: release
source_index:
  - "s4-film-chemistry-source-anchors.csv"
  - "evidence-index.jsonl"
---

# Passive film formation — domain reference

> 用途：建立从表面化学、膜层结构和 XPS 方法质量出发的机理证据边界。
> 明确区分"观察到表面/膜层变化"、"作者解释"和"Skill 推断"；
> 不能从耐蚀性单一改善直接宣布形成了特定钝化膜或机制。

## 1. 钝化膜判据

| 判据 | 直接证据要求 | 不可判定时 |
|---|---|---|
| 钝化膜形成 | 膜层化学证据（XPS 价态/深度剖面或等效）+ 电化学钝化区/低钝化电流 | 只有耐蚀性改善而无膜证据 → 不可宣布"形成钝化膜" |
| 膜层生长 | 时间/电位依赖的膜厚或电流衰减（PDM 参数或 ARXPS 膜厚） | 单点膜厚不能证明生长动力学 |
| 膜层缺陷 | 点蚀电位、亚稳态点蚀、击穿/再钝化证据 | 无击穿数据不得推断缺陷密度 |
| 膜层稳定性 | 时效/浸泡后膜化学与性能保持 | 短期改善不能外推长期稳定 |
| 激光—膜层关系 | 激光参数→热历史→膜层化学/结构的证据链 | 激光处理≠自动形成钝化膜；须区分氧化/重熔/清洗 |

来源追溯：钢种和膜层条目通过打包的 `s4-film-chemistry-source-anchors.csv`、
`evidence-index.jsonl` 与 `source-map.csv` 关联；材料牌号和表面状态缺失时不得
跨组推断。

## 2. 钢种差异与敏化边界（S4 基础）

| 钢种 | 关键边界 | 证据来源 |
|---|---|---|
| 304/304L 奥氏体 | 表面状态与敏化必须与名义牌号分开；304 vs 304L 比较非激光结果 | `doi:10.3390/met11010135`; `doi:10.1149/1945-7111/ac4bf7`; `candidate:P1-01-SENS-304-304L-DOERR-2016` |
| 304 敏化 | 铬贫化晶界、晶间腐蚀、亚稳态点蚀为独立机制；EPR/点蚀/膜指标不得合并 | `doi:10.20964/2018.07.74`; `doi:10.3390/ma15238543` |
| 316L 奥氏体 | Cr/Mo 膜化学与氯离子阻挡依赖环境与表面状态 | `doi:10.1016/j.electacta.2019.135159`; `doi:10.1149/2.0321911jes` |
| 316L 激光处理 | 织构密度/残余应力/清洗/老化可反转或掩盖激光收益；多道次 LSP 非单调 | `doi:10.3390/coatings9090592`; `doi:10.3390/coatings13122058`; `doi:10.3390/met12071215` |
| 铁素体/430 | 不可替代奥氏体 304/316L；LIPSS 可保持耐蚀但不改善；织构可恶化腐蚀 | `doi:10.1016/j.dib.2015.08.016`; `doi:10.1016/j.jmrt.2023.11.172`; `doi:10.3390/met15121387` |
| 马氏体 420/416 | 膜生长动力学、激光处理窗口 | `candidate:P1-01-420-PASSIVE-GROWTH-2002`; `doi:10.3390/ma10060595` |
| PH/双相 | 15-5PH/17-4PH/2205/2507 膜组成差异；酸钝化基线 | 使用打包索引中相应 `source_id` 的 PH/双相条目 |

来源追溯：上述钢种边界须通过打包的 `source-map.csv`、
`s4-film-chemistry-source-anchors.csv` 和 `evidence-index.jsonl` 逐条核验；
没有匹配来源时保留 `needs_user_review`。

## 3. 负结果与参数窗口（S4 反例）

- 激光织构/清洗/老化可反转或掩盖激光收益（`negative_or_conditional`）；每个例子须回到打包索引核验；
- 多道次 LSP 非单调（过处理降低耐蚀）；
- 织构密度非线性（AhuirTorres 2025 纹理密度/自由表面能反转）；
- LIPSS 保持耐蚀但不改善（Outon 2023 430）；
- 粗糙度改善但腐蚀不改善、润湿变化但膜化学不变（负相关反例）。

所有负例保留条件与时间点，不当作普遍反例定律；无法通过打包锚点解析的负例标记为
`source_unavailable`，不作为已核验事实使用。

## 4. 传统钝化对照

| 对照 | 可比条件 | 不可比条件 |
|---|---|---|
| 硝酸钝化 | 同钢种/同批/同电解液/同协议 | 不同钢种、不同电解液或协议 |
| 柠檬酸钝化 | 同上；记录浓度/温度/时间 | 酸种/浓度/温度不同 |
| 电抛光 | 表面状态可比（Ra/膜厚） | 电抛光膜 vs 激光膜机制不同 |
| 机械抛光 | 作为表面基线 | 机械抛光不是化学钝化 |

来源追溯：传统钝化对照使用 `s4-film-chemistry-source-anchors.csv` 和
`evidence-index.jsonl` 中的匹配材料、酸液、电解液、温度和测试协议；严格直接对比
不足时保留 `source_unavailable` 或 `deferred`，不冒充直接对照。

## 5. 已知缺口（不伪造）

- 激光 304/316L 同篇完整 raw XPS + fit table + residuals：原始导出未公开（`deferred`/作者索取）；
- 304L/316L 激光 vs 未处理同电解液 XPS 直接配对：当前多为 SLM-vs-wrought 或恶劣环境；
- 钢种特异溅射速率/厚度标定：Zhang 2024 用 Ta2O5 速率估算，保持 `derived_model`。

## 打包资源与追溯

- `s4-film-chemistry-source-anchors.csv`：膜化学、钢种和比较条件锚点。
- `evidence-index.jsonl`：逐条观察、状态和置信度索引。
- `source-map.csv`：统一来源元数据、可访问性和文件校验信息。

## 边界规则

- “钝化膜形成” requires both a film-chemistry/structure observation and a
  protocol-bounded passive-behavior observation; corrosion improvement alone is
  never sufficient.
- Steel-grade, heat-treatment/sensitization and surface-state boundaries stay
  attached to every claim. 304/304L, 316L, ferritic/martensitic, PH and duplex
  results are not interchangeable.
- Direct, author-interpreted, derived-model and agent-inferred statements stay
  separate in the analysis record. The known `deferred`, `source_unavailable`
  and `figure_only` cases remain visible.
