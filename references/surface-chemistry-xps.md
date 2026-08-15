---
title: "Surface chemistry and XPS — domain reference"
type: skill-domain-reference
skill: stainless-steel-laser-passivation
reference_id: surface_chemistry_xps
date: 2026-08-14
status: release
source_index:
  - "xps-source-manifest.csv"
  - "s4-film-chemistry-source-anchors.csv"
  - "evidence-index.jsonl"
---

# Surface chemistry and XPS — domain reference

> 用途：审查 XPS 方法质量、元素与价态证据、激光—膜层关系。
> 禁止从单一峰位或单条能级直接命名价态或机理。具体文献判断必须回到
> 打包的来源清单、锚点和证据索引。

## 1. XPS 方法质量

### 1.1 采集与校准

| 环节 | 必须记录 | 缺失/违规 → Skill 动作 |
|---|---|---|
| Survey | X-ray 线源/功率、分析器模式、通能、范围、步长、计数时间 | 先 survey 再选高分辨窗口 |
| High-resolution | 元素/能级、pass energy、step、dwell/scan、谱窗、重复位置 | 无 dwell/重复位置标 `not_reported` |
| 能量校准 | 参照物（Au 4f7/2、Cu 2p3/2、HOPG 等）+ 校准前后误差 | 只写 "corrected" 无误差 → 不可接受 |
| 荷电控制 | flood gun、接地、同片参照、事后平移区分 | 绝缘样品须 survey→C1s→HR→末端复测 |
| Adventitious C | 不可盲信 C1s=285.0/284.6 eV（Greczynski 2022 风险） | 无替代校准 → `charge_reference_uncertain` |

### 1.2 背景、拟合与定量

| 项目 | 可接受 | 失效信号 |
|---|---|---|
| 背景 | linear/Shirley/Tougaard 有物理理由 + 端点窗口 + 敏感性分析 | 背景敏感 → 报区间非单值 |
| 峰形 | Voigt/伪 Voigt、金属不对称、多重态 | 噪声峰当组分 → `overfit_risk` |
| FWHM | 同能级共享/受限 | 无化学理由大幅变化 → 重做模型 |
| 自旋轨道 | 固定分裂与面积比 | 面积比不守恒 → `SO_constraint_failure` |
| 多重态/卫星 | Fe 2p 参考谱+物理约束 | 单一 BE 命名 Fe(II)/Fe(III) → `single-line_assignment` |
| 拟合质量 | 原始谱+组分+残差+参数表+误差 | 只报 χ²/R² → 不足证模型唯一 |
| 定量 | RSF/传输函数/探测器线性校准 | 软件默认 RSF 直接比较 → `quantification_not_calibrated` |

### 1.3 溅射与深度

- Ar+ 还原/化学损伤：溅射后化学态先标 `sputter_affected`；无未溅射对照不得当原始膜剖面；
- 选择性溅射/偏析：记录离子能量/电流/角度/面积/温度/速率校准；优先 RBS/TEM 外部标尺；
- Preferential sputtering：深度/厚度必须带模型（MRI/衰减/速率标定）+ 不确定度；禁止 "sputter time→nm" 线性默认；
- ARXPS：厚度是几何+EAL/IMFP+层序+粗糙度+峰对的联合模型结果；报告角度范围与峰对敏感性。

来源追溯：方法和拟合条目通过打包的 `xps-source-manifest.csv`、
`s4-film-chemistry-source-anchors.csv` 与 `evidence-index.jsonl` 关联到
`source_id` 及页/表/图锚点。

## 2. 元素与价态证据（Fe/Cr/Ni/Mo/Mn）

| 元素/能级 | 全文示例锚点 | 报告状态 | 证据边界 |
|---|---|---|---|
| Fe 2p | Frontiers 2019 pp.6,9,T1 | Fe0 706.9；Fe(III) 氧化物 708.8–713.0；氢氧化物 711.8 | 7 组分+两层分配是模型；50% 假设需括号标注 |
| Cr 2p | Frontiers 2019 pp.6,9,T1 | Cr0 574.1；Cr(III) 氧化物 576.0–579.2；氢氧化物 577.2 | "无 Cr(VI)"是该谱结果，非普遍排除规则 |
| Mo 3d | Frontiers 2019；SIA 2002 | Mo0 227.6/230.7；MoIV 229.4/232.6；MoVI 232.2/235.3 | 重叠严重必须约束双峰；中间价态可混淆 |
| Ni 2p | Frontiers 2019 p.7；Crystals 2024 pp.12–13 | Ni0 852.8；Ni 氧化物 <0.5 at% | "未检出"是检测限结论 ≠ 不存在 |
| Mn 2p | OpenCorrJ 2009 pp.2–5 | 历史宽泛归属 | 无现代多重态/残差 → `historical_assignment_only` |
| O 1s | Frontiers 2019 p.7；Crystals 2024 p.12 | O2− 530.1、OH− 531.5、H2O 532.8 | 组分对背景/荷电/吸附水敏感；须交叉验证 |
| Cr/Fe、oxide/metal、hydroxide/oxide | Frontiers 2019 pp.8–10；Thermo AN126 | 比值依赖 RSF/背景/衰减/粗糙度/层模型 | 脱离模型复用 → 禁止 |

来源追溯：元素和价态示例必须使用打包索引中的 `source_id`、校准信息和锚点；
未能解析的谱图只保留为待核验提示。

## 3. 拟合失败与争议案例

- 背景敏感、过拟合、FWHM 自由漂移、SO 约束失败、单一 BE 命名价态；这些失败模式须在打包证据索引中保留相应锚点和状态；
- Yue 2023 氢充电超薄箔 CrN valley-fill 替代拟合反例（同步辐射 FlexPES）；
- 同一样品不同拟合方案冲突（C 包拟合歧义案例）；
- M-S 批判（La Mantia 2010）：单一频率 M-S 斜率解读需谨慎（B 包已取原文）。

## 4. 激光—膜层关系

| 证据链环节 | 直接证据 | 边界 |
|---|---|---|
| 激光→热历史→膜层 | 气氛/热历史/氧化膜/重熔层/缺陷/时效证据链 | 不能从末端耐蚀反推膜机理 |
| 激光氧化层 XPS | Lawrence 2016 304L 激光氧化层（figure_only） | 仅作读取示范，XPS 非主证据 |
| 直接激光 304L XPS | EDP 候选 `10.1051/metal/2013061` | 订阅限制 source_unavailable；不伪造 |
| 增材 316L XPS | Yue 2020（SLM vs 轧制）、Zhang 2024（LPBF 304L 深度剖面） | SLM 制造 ≠ 表面激光钝化 |

## 5. 公开数据与标准（方法输入）

- ISO 15472（能量校准）、18118（RSF）、19318（报告）、22581（adventitious C）、20579-1（样品处理）——metadata_only，不超出预览条款；
- NIST SRD 20 v5、NIST practical guides、JVST XPS Practical Guide 系列（仅按打包索引中可核验的条目使用）；
- XPSSurfA / TU Wien DBRepo / NIMS：原始谱需授权/登录，`metadata_only`。

## 6. 强制输出与禁止（S4 出口）

强制输出：source_id + SHA-256 + 页/表/图锚点；采集/校准/荷电设置；每能级组分 BE/FWHM/面积/SO/残差；reported/derived/author_interpretation/blocked 分层；溅射/ARXPS 参数。

禁止：单一峰位命名价态；溅射后低价态当原始膜剖面；χ²/R² 当模型唯一性；脱离 RSF/背景/衰减模型复用比值；figure_only 像素读数补数值。

## 打包资源与追溯

- `xps-source-manifest.csv`：XPS 来源元数据和全文状态。
- `s4-film-chemistry-source-anchors.csv`：元素/价态和方法锚点。
- `evidence-index.jsonl`：逐条观察、状态和置信度索引。
- `source-map.csv`：统一来源元数据和文件校验信息。

## 边界规则

- A binding-energy number is not a universal oxidation-state label. Keep the
  calibration reference, charge correction, fit model, background, constraints,
  residuals and detection-limit caveats with every peak claim.
- Sputtered/ARXPS spectra are method-specific profiles. Sputter damage,
  preferential sputtering and model-derived depth must remain explicit.
- The inaccessible direct-laser 304L XPS candidate remains
  `source_unavailable`; no value is reconstructed from the abstract or a
  neighboring paper.
