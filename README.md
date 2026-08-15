# 不锈钢激光钝化辅助 Skill

这是一个面向不锈钢激光钝化研究的证据意识型 Agent Skill，用于分析和比较激光工艺参数、表面化学、钝化膜、腐蚀性能、老化稳定性、测量质量及传统钝化对照。

本版本是可移植、已脱敏的 Skill 包，包含 schema、路由规则、确定性校验脚本和元数据示例源表。仓库不包含私有 PDF、本机路径、Zotero 条目键、个人标识或私人证据库。

## 安装

将本目录放置到：

```text
.agents/skills/stainless-steel-laser-passivation/
```

本包遵循 Agent Skills 目录结构：`SKILL.md` 是入口文件，`agents/openai.yaml` 提供可选的 OpenAI 兼容显示信息，`references/` 和 `scripts/` 保存可移植的领域资源与校验工具。

## 使用自己的证据

`references/` 中的 CSV/JSONL 文件只是小型示例。进行定量分析前，应替换为自己的 source map 和 evidence index。对于每个本地 PDF，应记录相对路径或用户配置的路径，并写入经过核验的 SHA-256；无法访问或信息不完整的来源必须明确标记为 `metadata_only` 或 `blocked`。

可选的 Zotero 校验路径默认关闭。如果使用该功能，必须通过 `--zotero-api-url` 显式提供你自己的端点；本包不会假定任何本地数据库地址。

## 确定性校验

在 Skill 根目录运行：

```bash
python scripts/run-stage6-suite.py --skill-root .
```

该命令检查 schema、路由、来源与证据链接、单位与可比性规则，以及非法样例的拒绝情况。如果没有提供新的模型运行结果文件，模型行为和路由行为会显示为 `NOT RUN`；确定性校验不能证明 Agent 永远遵守所有指令。

## 适用范围与非目标

本 Skill 用于不锈钢激光钝化领域的证据综合、比较和审计。文献检索/下载、PDF 提取、通用数据清理、DOE 设计、图件制作、论文写作、同行评审和投稿组装，应交给对应的通用 Skill。仓库中的示例源记录不得当作科学证据。

## 隐私与可移植性

请将个人 Zotero 导出文件、PDF、本机路径、凭据和实验室数据保存在仓库之外。私人证据包可以在本地维护，并通过用户自己的 source map 引用，但不要提交到 GitHub。
