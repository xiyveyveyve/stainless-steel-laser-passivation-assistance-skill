# 不锈钢激光钝化辅助 Skill

这是一个面向不锈钢激光钝化研究的证据意识型 Agent Skill，用于分析和比较激光工艺参数、表面化学、钝化膜、腐蚀性能、老化稳定性、测量质量及传统钝化对照。

本仓库已同步至 **2026-10-15 本地主线版本**，包含 `SKILL.md` 路由与跨批次合并纪律、L1–L7 文献证据综合与边界文档、1213 篇精读索引（`references/fullpool-read-record-index.csv`）、Mott-Schottky / PDM / DL-EPR 参数表、负向阈值与反例库（`references/laser-passivation-negative-thresholds.md`、`references/counterexample-registry.json`）、文献检索/实验设计/数据审计/矛盾模式检查单，以及 25 个确定性校验与审计脚本（含 `audit-experiment-design.py`、`build-search-query.py`、`flag-contradictions.py`）和 Stage 1–7 测试样例。

## 安装

将本目录放置到：

```text
.agents/skills/stainless-steel-laser-passivation/
```

本包遵循 Agent Skills 目录结构：`SKILL.md` 是入口文件，`agents/openai.yaml` 提供可选的 OpenAI 兼容显示信息，`references/` 和 `scripts/` 保存领域规则、索引与确定性校验工具，`evals/fixtures/` 包含 Stage 1–7 回归样例。

## 确定性校验与审计脚本

在 Skill 根目录运行：

```bash
python scripts/run-stage6-suite.py --skill-root .
```

新增 Stage 7 辅助脚本（检索词构造、实验设计审计、论文内部矛盾排查）：

```bash
python scripts/build-search-query.py --help
python scripts/audit-experiment-design.py --help
python scripts/flag-contradictions.py --help
```

## 隐私与忽略说明

本仓库为私有仓库全量同步，不包含 PDF 原文、本地数据库或个人凭据；临时草稿（`references/_tmp_*.txt`）、备份文件（`*.bak*`、`references/_sidecar_backup_*/`）以及 `__pycache__/` / `*.py[cod]` 等产物已通过 `.gitignore` 排除。
