# 丢失 case 恢复 + banshan skill 修改（2026-11-19）

## 问题原因

上一轮对块 `doxcnP63Mot5MbRSQY0Frpo75he`（「已修复缺陷验证用例」H1）执行了 `--command overwrite`，
该命令替换了该块及其下方的全部内容，导致「可直接点击的验证链接」「V2 功能覆盖矩阵」「预热/实时对比接口」
等 10 个 H1 章节（原 11 个 H1 变为 1 个）全部丢失。

## 恢复步骤

1. `+history-revert --history-version-id 43008`（revision 111）→ 文档恢复 11 个 H1
2. `block_insert_after` 追加表格格式 5 条缺陷用例（revision 116）
3. `block_insert_after` 追加换课逻辑说明 8 个 H2（revision 117）
4. `block_delete` 批量删除 34 个旧段落格式 block（revision 118）

## 最终文档结构（revision 118）

- 11 个 H1 全部恢复（如何开 V2 开关 / 预热怎么验 / 实时计算怎么验 / Apollo 配置 / 开关组合 / 可直接点击的验证链接 / 预热/实时对比接口 / V2 功能覆盖矩阵 / 接口与交互扫尾清单 / **已修复缺陷验证用例** / **换课逻辑说明**）
- 「已修复缺陷验证用例」下：5 条缺陷（A/B/C/D1/D2）均为两列表格格式
- 「换课逻辑说明」：8 个 H2（换课是什么/候选来源/保存展示/与勾选换年级关系/老链路vs V2/f6c12222修了哪一环/真实样例/需要产品确认的口径）

## banshan SKILL.md 修改

文件：`/Users/gaotu/.claude/skills-cold/banshan-case/SKILL.md`

在第 17 行通用格式说明之后插入「续班场景专用 case 格式」专节（新增约 32 行）：
- 明确续班相关用例一律用两列表格写每条 case
- 字段顺序：续班计划号 / 学员 ID / 班级课程 / 在读前置班(bizId) / 点击验证链接 / 验证功能 / 操作步骤 / 预期结果 / 实际结果
- 附对照格式示例
- 以飞书文档现有 case 为准，链接明确，非续班场景仍用通用格式
