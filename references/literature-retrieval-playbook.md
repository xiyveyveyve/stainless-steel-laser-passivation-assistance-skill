---
title: "文献检索与误捞过滤规则书"
type: skill-domain-reference
skill: stainless-steel-laser-passivation
reference_id: literature_retrieval_playbook
status: draft
date: 2026-10-14
source_basis: "全池 1215 篇精读（P0–P4）实测误捞统计"
---

# 文献检索与误捞过滤规则书

> **边界**：本文件定义**检索的领域规则**（检索式构建、误捞过滤、命中核验）。
> **执行**（实际检索、下载、PDF 提取）由通用 skill 或外部工具承担 —— **规则在此、执行在外**。

## 0. 本领域的实测误捞率

| 项 | 数值 |
|---|---|
| 全池精读 | **1215 篇** |
| 真正命中（has_target_data）| **314 篇** |
| 误捞 | **899 篇** |
| **误捞率** | **74.0%** |

**结论**：「不锈钢 + 激光 + 腐蚀」的字面组合远多于真正的「激光钝化」。**不设过滤的检索式会带来约 3/4 的无效阅读量。**

## 1. 十五类误捞模式

### (a) 「激光」角色错配 —— 最高频

laser 出现在文中但**不是激光表面处理/氧化/重熔/钝化**：

| 子类 | 判据 | 检索排除词 |
|---|---|---|
| 增材制造 | SLM / LPBF / L-PBF / DED / LMD / laser cladding / laser metal deposition | `additive manufacturing`、`selective laser melting`、`laser powder bed`、`SLM`、`LPBF`、`directed energy deposition` |
| 焊接 | laser welding / brazing / spot welding | `laser welding`、`laser brazing`、`laser-arc` |
| 冲击强化 | LSP / laser shock peening / laser peening | `laser shock`、`laser peening` |
| 淬硬/退火 | laser hardening / laser annealing | `laser harden`、`laser anneal` |
| 织构 | LIPSS / laser texturing / dimple | `LIPSS`、`laser textur`、`laser-induced periodic` |
| 抛光/打标/切削 | laser polishing / marking / cutting | `laser polish`、`laser mark`、`laser cut` |
| **分析仪器** | APT 场蒸发 / 共聚焦 / μ-Raman 光源 / 激光散斑 / 轮廓仪 / 开尔文探针 | `laser confocal`、`Raman`、`laser speckle`、`laser profilometry`、`laser pulse` (APT)、`Kelvin probe` |

**注意**：laser texturing / cladding / remelting 也可能是**真命中**（见 §4 的边界），不能一律排除 —— 排除的是「激光只是成形手段」的情况。

### (a′) 「passivation」同名不同物

| 子类 | 判据 | 排除词 |
|---|---|---|
| 化学钝化 | Cr(VI) / HNO₃ / 柠檬酸 / 硝酸浸泡 | `nitric acid passivation`、`citric acid`、`Cr(VI)`、`chromate` |
| 热敏化破坏 | sensitization / Cr 碳化物析出 | `sensitization`、`Cr23C6` |
| 间隙固溶去膜 | S 相 / 渗氮 / 渗碳 | `S-phase`、`nitriding`、`carburizing` |
| 合金元素 | passivation-activating elements | `passivation-activating` |
| **超疏水有机涂层** | FAS / PFOTES / 硅烷自组装 | `superhydrophobic`、`FAS`、`PFOTES`、`fluorosilane` |

**纪律**：**`passivation` 必须与激光工艺词同现**，否则不构成激光钝化证据。

### (b) 期刊域错配

整批可剔除的期刊/文献类型：
```
Wear · Tribology International · J. Nucl. Mater. · Nuclear Eng. Design · NDT&E International
Micron · Spine Journal · Sci. Total Environ. · Surface Science · Metal Powder Report 摘要页
LCA 可持续性 · 核燃料性能 · 金属切削/摩擦学刊 · MDPI ISBN 图书 · TMS/HSLA 会议集
Oxid. Met. · Metall. Microstruct. Anal. · Acta Metall. Sin. · EPJ Nuclear · Res. Biomed. Eng.
ASME PVP · NATO SPS · 手册章节 · 综述/讲座体 · 文摘汇编页 · ASTM STP
```

### (c) 姊妹文献二手

数据/曲线不在本文，而在其引用的文献里。判据：全文唯一相关论断带引用标记，或图注写 `reprinted from` / `adapted from`。

### (d) 「电解质」只是制样液/浸泡介质
```
制样液：电解抛光液、金相蚀刻液（草酸/NaOH 电解蚀刻）、TEM 双喷液
工艺槽：酸洗/钝化膏/着色槽
浸泡介质：盐雾、浆料、体液（SBF/PBS）、饮用水、高压水、超临界水、熔融金属（LBE）、高温油相（环烷酸）、干燥盐沉积（冷凝液）、磨耗介质
```

### (e) 材料不是不锈钢（Cr < 10.5%）

低合金钢 / 模具钢 / 铸铁 / 锆合金 / **镍基合金（Ni 为基体）** / 碳素钢 / 船板钢。

**判据**：**用实测值**，Cr ≥ 10.5 wt% **且 Ni 非基体**。仅牌号 → 记 `by_designation_only`。

### (f) 充氢液被当电解质
```
0.5 M H2SO4 + 硫脲 / NH4SCN / Na4P2O7 · 重水充注 · 气态 H2 高压充注
```

### (g) 作者自引腐蚀期刊 ≠ 本文含腐蚀数据

引用了腐蚀期刊只说明作者在引用，不说明本文有腐蚀数据。

### (h) review / 图书 / 手册 / 讲座体

**自动判据**：`Data availability: Not applicable` / `No new data were created` / 无 Methods 章节 / 全文 >90% 是参考文献 / 将来时叙述（`We will review`）。

### (i) 文摘汇编页 / 会议摘要

单页、无原始数据、页码形如 `p. XXXX-XXXX` 且 ref-count = 0。

### (j) 牌号出现在参考文献内 / 被误标为 mild steel

**判据**：牌号只出现在参考文献标题里；或正文把 304/316 标为 `mild steel`。

### (k) 混合参比

同文中 Ag/AgCl + SCE + vs OCP 混用且无换算 → 跨文献比较前必须先解决标度。

### (l) 勘误 / 社论 / 书评 / 图题张冠李戴

首行带 `Erratum to:` / `Foreword` / `Book Review`；或图题中的材料与正文不符（见 `paper-internal-contradiction-patterns.md` M10）。

### (m) 纯 ML / QSAR / DFT / MD

汇编他人数据、或物理对象是孤立原子复合物能，**不是钝化膜**。

**判据**：标题/metadata 含 `machine learning` / `XGBoost` / `SHAP` / `DFT` / `molecular dynamics` / `QSAR`，且全文无 E_corr/E_pit/R_ct。

### (n) 交流电位降 / ΔU 被误当电化学

Matelect 等**裂纹扩展仪**的 AC potential drop 是断裂力学测量，不是极化。

### (o) 文档抓错

.txt/.pdf 实为厂商规格书 / 补充材料 / 别的 DOI 的正文。

**判据**：文本 < 200 行、无 Abstract/Methods 章节、DOI 与内容不匹配、体积 < 500 B 的失败桩。

## 2. 全文提取与 grep 陷阱

### 2.1 grep 陷阱词表（大小写不敏感误捕）

| 正则 | 误捕来源 | 正确语境 |
|---|---|---|
| `SCE` | con**sce**rring、**sus**ce**pt**ibility、**sce**nario、ScienceDirect、CRT cert | 饱和甘汞电极 |
| `EPR` | repre**epr**esentation、electr**ON**、proc**ess**Ed、sch**E**matic R EPResentation | 电化学再活化 |
| `Rp` | **Rp0.2**（屈服强度）、mo**rp**hology、ru**p**ture | 极化电阻 |
| `sensitiz` | crack sensitivity、冶金义敏化 | DL-EPR 敏化测试 |
| `polariz` | spin **polariz**ed（DFT） | 极化 |
| `Faraday` | **Faraday cup**（加速器） | 法拉第定律 |
| `GPR` | **G**aussian **P**rocess **R**egression | 地面穿透雷达 |
| `CERT` | **c**onstant **e**xtension **r**ate **t**est ≠ con**sce**rring | —— |
| `remel` | electroslag **remelting**（ESR 炼钢） | 激光重熔 |
| `passivat` | 化学钝化 / 热破坏 / 合金元素 / 有机涂层 | 激光钝化 |

### 2.2 断词假阳性
```
con-sce-ring   → 实为 concerning
sce-nario      → 实为 scenario
repre-sentation→ 实为 representation
pre-nss-ure    → 实为 pre-NSS-ure（NSS = neutral salt spray）
electrol-/yte  → 断开后 grep 漏检
```

### 2.3 英式拼写漏检

通道 B 正则须同时匹配 `sensitiz|sensitis` —— `maco.19950460603` 的 `sensitised` 会被 `sensitiz` 静默漏检。

### 2.4 控制字符检查（防乱码假阴性）

**通道判定的 grep「零命中」必须配合控制字符占比检查**：

```python
ctrl = sum(1 for ch in text[:20000] if ord(ch) < 32 and ch not in '\n\r\t')
if ctrl / 20000 > 0.05:   # >5%
    verdict = 'document_corrupt'   # 不判「通道 A」
```

**实证**：本池 618 篇中 2 篇中招（2001–2002 年 Elsevier *Corrosion Science*，3B2 Total Publishing / Acrobat Distiller，Type1 子集字体无 ToUnicode）。其中 `s0010-938x_00_00114-1` 的 grep 零命中**掩盖了一篇真正的通道 A 命中**。

**修复配方**：
1. 读 `/Encoding /Differences` → 字形名 `/Cnnn` → `chr(int(nnn))`（**nnn 是十进制不是八进制**）
2. 符号子集须手工覆盖：`C100/C133=δ`、`C134=(`、`C136=)`、`C176=⇕`、`C211=ℜ`
3. 坑：页 `/Resources` 是内联 dict 不是 xref；`/C40._` 这类带尾缀 token 必须用 `re.match` 且**每 token 都 code += 1**，否则码 ≥51 之后整体错位一格（表现为 O→W、CO₂→CW2、5kW→5Hz、stainless→st%ll）

### 2.5 单位字符吞没

| 症状 | 实际 | 案例 |
|---|---|---|
| `mm` 实为 µm | µ→m | `6.971.8 mm`、EBSD `0.15–0.74 mm`、`5 lm` |
| `mg` 实为 µg | —— | —— |
| `8160C` | 816 °C | 上标被吞 |
| `K1c 0.56MNm-3/2` | 0.56 MPa·m^½ | 单位压缩 |
| `35 °C` | −35 °C | 负号被吞 |
| `pH ¼ 5.7` | pH ≈ 5.7 | ¼ = ≈ |
| `3 £ 1023` | 3×10⁻³ | £ = × |

## 3. 画像关键词的核验纪律

### 3.1 核心规则

> **画像关键词来自「全文出现」，不是「本文实测」。**

多篇画像标 `Mott-Schottky` / `XPS` / `EIS`，实际是**参考文献里出现**或**泛述**。

### 3.2 实证

| 文献 | 画像声称 | 实际 |
|---|---|---|
| `apsusc.2018.10.150` | 含 Mott-Schottky | 全文仅 1 次，在**参考文献 [35]** |
| `corsci.2020.108480` | 含 Mott-Schottky | 全文仅 1 次，在**参考文献 [48]** |
| `apsusc.2019.144495` | 含 XPS | 是**二手**（本文做 AES，XPS 引 [39,54]）|
| `corsci.2008.06.019` | 含 EIS/M-S | 全文 0 命中 |
| `ijoes.2025.101264` | 含 XPS | 引用文献 [60] 的转述 |

### 3.3 操作

1. 对每个画像字段，检索它在文中出现的位置
2. 判断是**本文方法节**、还是**引言/参考文献**
3. 若为后者 → 记 `profile_miss`（画像落空）
4. **不得据画像字段直接入库**

## 4. 检索式构建模板

### 4.1 三层结构

```
层 1（材料）  AND  层 2（工艺）  AND  层 3（表征/电化学）
                        NOT 层 4（排除项）
```

### 4.2 各层词表

**层 1 · 材料**
```
"stainless steel" OR "316L" OR "304L" OR "304" OR "316" OR "2205" OR "2507"
OR "duplex stainless" OR "super duplex" OR "17-4PH" OR "AISI 420" OR "AISI 430"
OR "SS 316L" OR "SS304"
```

**层 2 · 激光工艺（须与「表面处理」语义绑定）**
```
"laser surface" OR "laser passivation" OR "laser oxidation" OR "laser remelting"
OR "laser surface melting" OR "laser surface remelting" OR "LSM" OR "LSR"
OR "laser shock peening" OR "laser texturing" OR "laser cladding"
OR "femtosecond laser" OR "nanosecond laser" OR "picosecond laser"
OR "strong-field laser" OR "filamentation"
```

**层 3 · 表征/电化学**
```
"corrosion" OR "passive film" OR "passivation" OR "pitting"
OR "EIS" OR "electrochemical impedance" OR "polarization" OR "potentiodynamic"
OR "Mott-Schottky" OR "XPS" OR "photoelectron spectroscopy"
OR "pitting potential" OR "Ecorr" OR "icorr" OR "Rct"
```

**★ 层 4 · 排除词（针对 15 类误捞）**
```
NOT ("additive manufacturing" OR "selective laser melting" OR SLM OR LPBF OR "powder bed"
     OR "directed energy" OR DED OR LMD OR "laser metal deposition")
NOT ("laser welding" OR "laser brazing" OR "spot welding" OR "laser-arc")
NOT ("laser hardening" OR "laser annealing" OR "laser polishing" OR "laser marking")
NOT ("superhydrophobic" OR "FAS" OR PFOTES OR "fluorosilane" OR "self-assembled monolayer")
NOT ("nitric acid" OR "citric acid" OR chromate OR "Cr(VI)")
NOT ("sensitization" OR "Cr23C6" OR "DL-EPR" OR "degree of sensitization")
NOT ("salt spray" OR "neutral salt spray" OR "immersion test" AND "simulated body fluid")
NOT ("liquid lead-bismuth" OR LBE OR "lead-bismuth eutectic")
NOT ("supercritical water" OR "PWR" OR "BWR" OR "pressurized water reactor")
NOT ("molten salt" OR "hot corrosion" OR "fireside" OR "deposit corrosion")
NOT ("hydrogen charging" OR "hydrogen embrittlement" OR thiourea OR "cathodic charging")
NOT ("neural network" OR "machine learning" OR XGBoost OR SHAP OR QSAR OR DFT OR "molecular dynamics")
NOT ("acoustic emission" OR "potential drop" OR "crack growth" OR "fretting" OR "erosion-corrosion")
NOT ("nuclear fuel" OR "cladding" AND "fuel performance")
```

### 4.3 用词示例

```
( "stainless steel" OR "316L" OR "304L" )
AND ( "laser surface" OR "laser passivation" OR "laser remelting" OR "laser oxidation"
      OR "laser shock peening" OR "femtosecond laser" OR "nanosecond laser" )
AND ( "corrosion" OR "passive film" OR EIS OR "pitting potential" OR "Mott-Schottky" OR XPS )
NOT ( "additive manufacturing" OR SLM OR LPBF OR "laser welding" OR "laser cladding"
      OR superhydrophobic OR "nitric acid" OR "liquid lead-bismuth" OR "supercritical water" )
```

### 4.4 生成工具

`scripts/build-search-query.py` —— 输入研究问题，输出上述结构的检索式

## 5. 命中后的核验清单

拿到一篇候选文献，按序核验：

| # | 核验项 | 通过条件 | 不通过则 |
|---|---|---|---|
| 1 | 文本层可用性 | 控制字符 <5% | 重建文本（§2.4） |
| 2 | 文档身份 | 有 Abstract/Methods/References | 判 (o) 文档抓错 |
| 3 | 期刊域 | 不在 §1(b) 黑名单 | 降级或剔除 |
| 4 | 材料 | **实测** Cr ≥ 10.5% 且 Ni 非基体 | 判 (e) |
| 5 | 激光角色 | 表面处理/氧化/重熔/钝化 | 判 (a) |
| 6 | 电解质 | 真腐蚀介质，非制样液/浸泡液 | 判 (d) |
| 7 | 画像字段 | 逐项确认「本文实测」 | 记 `profile_miss` |
| 8 | 参比 | 有标准标度且内充液注明 | 判 (k) |

## 6. 覆盖率反查纪律

### 6.1 规则

> **派发前必须断言 `pool_ids − read_ids == ∅`**，而不是「当前批次队列已清空」。

### 6.2 实证教训

本池 P3 收官后做覆盖率反查，发现 **102 篇从未进入任何精读批次**，其中 **79 篇属 L7（laser ∧ XPS）** —— 是本池**密度最高的一批**。

**根因**：文本渲染清单与层分类清单是**两次独立生成**的，二者交集从未校验。这是一类**不报错、只漏判**的过程缺陷。

### 6.3 两条必做检查

1. **派发前**：`pool_ids − read_ids == ∅`（全池覆盖率反查，非当前队列）
2. **每轮收尾**：`read_ids − skill_ingested_ids == ∅`（精读成果 → skill 汇入 对账）

### 6.4 漏检的另一个来源：画像层划分偏差

若画像按「关键词层」分类（L1–L7），必须**独立验证**该分类与文本渲染清单的交集。本池 L1–L6 由画像生成，L7 是事后补算的，二者最初未对账。

## 7. OA 全文获取途径（绕过订阅墙）

### 7.1 ★ 首选：Europe PMC fullTextXML

```
https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/fullTextXML
```

**为什么有效**：纯 REST API，返回 XML 全文，**不需要 JS 渲染、不受 Cloudflare 拦截**。

**流程**：
1. 用 OpenAlex（`api.openalex.org/works/doi:{doi}`）或 Unpaywall（`api.unpaywall.org/v2/{doi}?email=...`）查 `pmcid`
2. 用 Europe PMC `fullTextXML` 取全文
3. 剥 XML 标签转纯文本

**实证**：`s41377-025-01952-5`（PMC12496454）与 `mi13071089`（PMC9317285）由此获取。

### 7.2 各途径效果对照

| 途径 | 结果 |
|---|---|
| 直连出版商 | SSL UNEXPECTED_EOF（网络阻断）|
| 代理（HTTP/SOCKS5）| 视分流规则，出版商域名可能被分到直连 |
| MDPI 直链 | 403 Cloudflare |
| PMC/HAL PDF 直连 | 返回 HTML（`Making sure you're not a bot!`）|
| **Europe PMC fullTextXML** | ✅ **成功** |

### 7.3 若仍失败

- 检查代理分流规则（`DOMAIN-SUFFIX,wiley.com,PROXY` 等）
- 用 Semantic Scholar（`api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf`）查其他托管点
- 用 CORE / OpenAIRE / DOAJ 查机构库副本

## 8. 快速判废流程（一分钟）

```
1. 文本 < 200 行？            → (i)/(l)/(o) 判废
2. `laser` 零命中？            → 无激光，判废
3. `laser` 只在参考文献？      → (a)/(j) 判废
4. 控制字符 >5%？             → document_corrupt，重建文本
5. 材料 Cr < 10.5% 或无实测？  → (e) 判废或 by_designation_only
6. 唯一 electrolyte 是制样液？ → (d) 判废
7. 无 Methods 章节？           → (h) 判废
8. 以上全过 → 进入精读
```
