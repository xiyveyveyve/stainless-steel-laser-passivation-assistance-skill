---
title: "Laser process metrology — domain reference"
type: skill-domain-reference
skill: stainless-steel-laser-passivation
reference_id: laser_process_metrology
status: release
date: 2026-08-14
source_index:
  - "laser-process-source-manifest.csv"
  - "laser-process-source-anchors.csv"
  - "source-map.csv"
  - "evidence-index.jsonl"
---

# Laser process metrology — domain reference

## Contents

- 统一参数字段
- 剂量与计量公式
- 处理类型边界
- 可比性审查
- 领域来源整理
- 已知缺口
- 打包资源与追溯
- 边界规则

> 用途：判断激光工艺报告是否足以复现、不同研究是否可比较，以及处理是否
> 可称为"激光钝化"。所有规则保留打包来源锚点；缺失字段不得用默认值填充。

## 1. 统一参数字段（激光术语与过程分类）

| field | definition / unit | mandatory evidence | common failure |
|---|---|---|---|
| `laser_mode` | CW, ns, ps, fs, burst, strong-field/filament, LSP | source text and laser model | calling all pulsed lasers "average power" only |
| `wavelength_nm` | central wavelength; preserve bandwidth if reported | page/section anchor | mixing fundamental and harmonic wavelength |
| `pulse_duration_s` | FWHM or stated pulse width; preserve definition | source wording | treating rise time or gate width as pulse width |
| `repetition_rate_Hz` | pulse frequency | source/table anchor | confusing scan frequency with pulse frequency |
| `pulse_energy_J` | measured or derived from power/repetition rate | formula and loss assumption | using nominal power without duty/loss note |
| `spot_definition` | Gaussian 1/e², FWHM, 4-sigma, top-hat physical edge, effective ablation diameter | measurement method | mixing 4-sigma and FWHM as the same diameter |
| `spot_diameter_m` | diameter in the declared definition window | beam-profile figure/table | using focal length or nozzle diameter as spot size |
| `beam_shape` | Gaussian, elliptical Gaussian, top-hat, donut, measured profile | profile image/fit | applying circular area to elliptical/donut beam |
| `average_power_W` | time-averaged delivered power | power meter/measurement protocol | replacing with peak power |
| `peak_power_W` | pulse energy / pulse duration; only for pulsed source | pulse duration and energy | using CW power in peak-intensity formula |
| `fluence_J_cm-2` | energy per area; state single-pulse or accumulated | spot area and pulse energy | reporting "energy density" with no area definition |
| `scan_speed_m_s-1` | stage or beam relative speed | method/setting | confusing feed speed with pulse spacing |
| `pulse_step_m` | v/f for line scan | speed and repetition rate | calculating from average line spacing |
| `hatch_m` | line-to-line spacing | scan strategy | calling hatch "overlap" without diameter |
| `pulse_overlap_pct` | pulse-to-pulse overlap; direction and spot definition required | Delta-x, D and model | one-dimensional formula ignores hatch direction |
| `line_overlap_pct` | line-to-line overlap | hatch, D and beam shape | using pulse overlap for line overlap |

来源追溯：参数字段通过打包的 `laser-process-source-manifest.csv`、
`laser-process-source-anchors.csv` 和 `evidence-index.jsonl` 关联到来源锚点；
不以未打包的矩阵文件作为运行时依赖。

## 2. 剂量与计量公式（保留原文参数与单位）

| id | formula | assumptions / units | source anchor |
|---|---|---|---|
| F-01 | `E_pulse = P_avg (1-L) / f` | P in W, loss L as fraction, f in Hz | Fox Eq.9, p.6 |
| F-02 | `F_pulse = E_pulse / A_spot` | single-pulse fluence; J/cm² after area conversion | Fox Eq.10, p.6 |
| F-03 | `A_circle = pi D² / 4` | circular effective spot only; D in same length unit | Fox Eqs.7/10, p.2/6 |
| F-04 | `Delta_x = v / f` | line scan; v in m/s, f in Hz | Fox Eq.1 definition, p.1 |
| F-05 | `OL_x(%) = (1 - Delta_x/D) 100` | rectangular/near-small-step approx; one scan direction only | Fox Eq.1, p.1 |
| F-06 | `F_acc = E_pulse / (Delta_x Delta_y)` | accumulated fluence for rectangular scan cell | Fox Eq.6, p.2 |
| F-07 | `n_acc = F_acc A_spot / E_pulse = A_spot/(Delta_x Delta_y)` | average pulses per point; effective spot area required | Fox Eq.7, p.2 |
| F-08 | `OL_avg(%) = (1 - 1/n_acc) 100` | average overlap, not a local overlap map | Fox Eq.8, p.2 |
| F-09 | `E_line = P_avg / v` | line energy J/m for CW or time-averaged pulsed | derived; assumptions must be declared |
| F-10 | `E_area = P_avg/(v h)` | areal dose J/m²; h is hatch in m | derived from scan-cell geometry |
| F-11 | `P_peak = E_pulse/tau` | pulsed source; tau is stated pulse duration | model-derived; do not use for CW |
| F-12 | `F0_Gaussian = 2 E_pulse/(pi w²)` | peak fluence for circular Gaussian, w = 1/e² radius | Gaussian model; verify profile definition |
| F-13 | `u_c = sqrt(sum u_i²)`; `U = k u_c` | independent standard uncertainties; k often 2 | NIST SP250-87 pp.15-18 |

可复算计算例（Fox 开源例）：D = 79 µm, P = 26.7 mW, L = 10%, f = 250 Hz, n_acc = 1 →
`E_pulse = 96.12 µJ`, `F_pulse = 1.96 J/cm²`, `Delta_x = Delta_y = 70 µm`, `OL_avg = 0%`
（公式和示例的来源锚点见打包的 `laser-process-source-anchors.csv` 与
`evidence-index.jsonl`；重算时保留原始单位和假设。）

来源追溯：公式记录必须关联打包索引中的 `source_id` 与页/表/图锚点。

## 3. 处理类型边界（判别规则与反例）

| 处理 | 判别要点 | 不可判定时 |
|---|---|---|
| 激光钝化 | 表面形成保护性氧化膜/钝化膜 + 耐蚀性证据 + 膜化学证据 | 只有耐蚀性改善而无膜证据 → 不可宣布"钝化膜形成" |
| 激光氧化 | 气氛（空气/O2）主导的氧化膜生成，未证明钝化作用 | 氧化膜 ≠ 钝化膜 |
| 激光清洗 | 去除污染物/氧化皮，无新增保护膜 | 清洗改善 ≠ 钝化改善 |
| 激光标记 | 着色/标识，可能伴随氧化但非为钝化目的 | 标记文献不得直接充当钝化证据 |
| 激光纹理化 | 几何形貌改变，润湿性/粗糙度主导 | 纹理化改善润湿 ≠ 钝化 |
| 激光烧蚀/雕刻 | 材料去除，ablation 边界 | 烧蚀参数不得移植到钝化 |
| 激光重熔/抛光 | 熔融重凝、表面平滑 | 重熔层 vs 钝化膜需区分 |
| LSP 冲击强化 | 机械冲击引入压应力 | 应力改善 ≠ 化学钝化 |

边界反例（DF-01~DF-12；逐条锚点见打包索引）：
- DF-08：不能把 nominal focus 当作样品面稳定光斑（Gaikwad 2022 Ophir Nanoscan 2 实测支持）；
- 焦平面漂移：63–421 µm 光斑范围（`doi:10.1016/j.matdes.2022.110919`），能量通量/孔隙率后果；
- 表面状态依赖 fluence 阈值（`doi:10.1007/s40516-022-00199-x`）：单脉冲、表面状态明确才可比。

## 4. 可比性审查（最小复现字段与禁区）

最小复现字段（先按本节的 critical/noncritical 分类，不把所有缺失字段归为同一状态）：
`laser_mode + wavelength + pulse_duration + repetition_rate + pulse_energy(或平均功率+损耗) + spot_definition + spot_diameter + beam_shape + scan_speed + pulse_step/hatch + overlap(方向+直径) + 扫描次数 + 焦平面 + 气氛 + 前/后处理 + 吸收/入射区分`

### 四状态判定优先级

按以下顺序判定；每次比较都要在 `reasons` 中写明缺失、冲突或条件化字段：

| 优先级 | 状态 | 判定条件 |
|---|---|---|
| 1 | `not_comparable` | 来源和关键字段已足以确认存在关键材料、过程类别或剂量定义冲突；例如钢种/热处理边界不匹配、处理类别不同，或 spot/overlap/累计剂量定义已确认不一致。 |
| 2 | `needs_user_review` | 尚不能确认冲突，但关键字段缺失、定义不明，或来源/页表图锚点未解析；spot 定义、spot 直径/光束形状、overlap 方向与公式、功率平面/损耗、脉冲/线/累计剂量属于关键字段。此状态优先于 `partially_comparable`。 |
| 3 | `comparable` | 关键字段完整，材料/过程/剂量定义匹配，来源锚点已核验，且没有会改变当前问题的已知差异。 |
| 4 | `partially_comparable` | 来源和锚点已核验，关键定义足够，仅存在已知非关键差异，或差异已被明确条件化；必须同时写出比较成立的条件和不能外推的范围。 |

关键字段是会改变剂量、热历史或材料响应解释的字段；非关键字段只能在说明其不会改变当前比较问题后标记为 noncritical。
`required_fields_complete: false` 本身不能决定状态：若缺的是关键字段，使用 `needs_user_review`；若仅缺已论证的非关键字段，才可使用
`partially_comparable`。未解析锚点不得被当作已核验来源。

### 跨论文/跨牌号比较门槛

允许进入同一比较子组必须同时满足三类相容：

1. **材料边界**：钢种/牌号、热处理或敏化状态、表面状态相容；
2. **激光工艺/剂量定义**：处理类别、关键参数、spot/overlap、功率平面和剂量定义相容；
3. **测量/测试协议**：电解液、参比电极、扫描或频率协议、工作面积、环境、重复数及误差/不确定度相容。

比较单元的陈述必须直接携带上述条件；缺失项不能只放在 missing-fields 列表中，须写为
`not_reported`/`blocked` 并按四状态规则降级。三类边界任一未解析，不得进入
`comparable` 子组。

比较禁区：
- 不同 spot 定义（4-sigma vs FWHM vs 1/e²）不得混算直径；
- 圆形面积不得套用椭圆/donut 光束；
- 只给 overlap% 而无直径/方向/公式 → `overlap_not_reproducible`；
- 只给图像而无标尺/profile convention → `figure_only`；
- 名义功率无 duty/loss 说明 → 不得自动生成 fluence；
- 单脉冲 fluence 不得自动推断 accumulated fluence；
- 缺失字段按上表分类；不得用 `partially_comparable` 掩盖关键定义缺失。

来源追溯：比较结论必须回链 `laser-process-source-anchors.csv`、
`laser-process-source-manifest.csv` 和 `evidence-index.jsonl`；没有匹配锚点时保留
`needs_user_review` 或 `source_unavailable`。

## 5. 领域来源整理（来源锚点索引）

主来源集（详见打包的 `laser-process-source-manifest.csv` 和
`laser-process-source-anchors.csv`）：
- 316L 动态吸收率/功率计标定：`doi:10.1007/s00170-024-14008-6`（Wittemer 2024, ISS/BRS/beam-caustic）；
- 316L 1064 nm 纳秒烧蚀计量：`doi:10.3390/nano12020232`（Hribar 2022, M²-based spot/fluence/overlap + 校准能量计/光电二极管 + 扫描头输出端功率计）；
- 焦平面漂移 profiler：`doi:10.1016/j.matdes.2022.110919`（Ophir Nanoscan 2, 1/e² Gaussian）；
- 单脉冲/表面状态 fluence 阈值：`doi:10.1007/s40516-022-00199-x`（Al-Mahdy, 4–614 µJ）；
- 不锈钢纹理化（257 nm/350 fs）：`doi:10.1039/C8RA01774C`（spot 估算，非 profiler 实测 → 标注 caveat）；
- 可迁移计量证据（非 304/316L 直接）：`candidate:Wuppertal-2023-ODS-laserAM-metrology`（功率校准曲线/焦斑设置）、`candidate:DCU-2018-316L-cylindrical-pins`（参数矩阵，spot 校准不完整）；
- 方法/标准：NIST SP250-87（激光束直径测量，不确定度 F-13）。

引用规则：任何跨论文比较必须保留材料/工艺边界；不把 ODS/AM、焊接或粉床来源冒充平面 304/316L 钝化实测。

## 6. 已知缺口（不伪造）

- 平面 304/316L 样品面完整实测 beam map、目标工件处 delivered power、表面状态匹配的绝对 absorptance、完整 M² z-scan、多道次热历史——实验室实测类，`deferred`（用户未返校）；
- ISS 反射边界未量化时仅作定性吸收特征，不得当作绝对 absorptance。

## 打包资源与追溯

- `laser-process-source-manifest.csv`：激光工艺来源元数据。
- `laser-process-source-anchors.csv`：参数、公式和反例锚点。
- `source-map.csv`：统一来源元数据、可访问性和文件校验信息。
- `evidence-index.jsonl`：逐条观察、状态和置信度索引。

## 边界规则

- `F-01` is valid only when the power plane is explicit. If `P_avg` is a
  workpiece-plane delivered value, use `L = 0` and record that assumption. If
  it is a source or scan-head value, a measured/literature loss fraction is
  required; otherwise do not derive pulse energy or fluence.
- `pulse_overlap_pct` and `line_overlap_pct` are separate fields. A single
  overlap percentage without direction, spot definition and formula is
  `needs_user_review`, not a reproducible dose.
- The source-map statuses `same_process`/`limited` map to the Skill's
  `comparable`/`partially_comparable` statuses. `overlap_not_reproducible` and
  `figure_only` remain reasons, not new status values.
- `laser_passivation_candidate` is a candidate process label only. A final
  claim that a passive film formed still requires surface-chemistry or film
  evidence; corrosion improvement alone is insufficient.
- Source IDs in this reference must resolve through the packaged `source-map.csv`
  and `evidence-index.jsonl`; source-manifest entries are evidence-group labels,
  not permission to infer unreported parameters.
