---
title: 技术方案交付记录 · 膨胀券预报名优化(A) + 小班课学员人数上限修改(B)
tags: [需求, 交付记录, 技术方案]
date: 2026-10-29
---

# 技术方案交付记录（2026-10-29）

> 仅记录证据，不复制方案正文。相关需求本地归档：`续班预报名使用膨胀券`。

## 1. 两篇飞书技术方案

| | A | B |
|---|---|---|
| 需求 | 【PRD】膨胀券预报名优化-推荐和外显抵扣金额 | 小班课学员人数上限修改 |
| 飞书 URL | https://gaotuedu.feishu.cn/wiki/Kgphw2GhciYHuvkyy03coeHUnOh | https://gaotuedu.feishu.cn/wiki/JlJcwTRtLiwaxJk1Yhuc9UQznIa |
| docx token | `VmHWdzTiHonakuxrVSOcp0pWncg` | `RAkmdgC9ZoyntNxPmsHcEm9DnOd` |
| 放置父节点 | PRD A 子级：`TIGtweLV4iWdYtksyqNcWhIhnYb`（PRD A 自身父节点 = `N58DwzUDoi3sK3k1nCqcPOBMn3d`，即已有需求「续班预报名使用膨胀券」的基础 PRD） | 「教学服务」根：`G3FgwZMidiPLHNk34Occadv0ngc`（space `7501250181476663298`）；PRD B 所在 space `7521677387233722372` 无写权限（code 3380004） |
| 回读标题 | 技术方案 · 膨胀券预报名优化（推荐规则 + 外显抵扣金额） | 技术方案 · 小班课学员人数上限修改 |
| 回读正文字符数 | 6324 | 4694 |

回读命令：`lark-cli docs +fetch --doc <token> --doc-format markdown`（字符数取返回 `data.document.content` 长度；两篇均含第 9 节「目标仓库与分支」，revision_id=4）。

## 2. student-data 校验

```
$ git -C /Users/gaotu/IdeaProjects/JavaProject/student-data merge-base --is-ancestor origin/release HEAD
exit=0
$ git -C /Users/gaotu/IdeaProjects/JavaProject/student-data branch --list 'feature-*'
exit=0
$ git -C /Users/gaotu/IdeaProjects/JavaProject/student-data rev-parse HEAD
91012878d692119e79fb7d14baa1bab594c9534d
```

`branch --list 'feature-*'` 输出含本需求两分支：`feature-xuban-presale-expand-opt`、`feature-small-clazz-limit-and-search`（当前 `*` 指向 `feature-xuban-dify-offline`，未改动）。

## 3. 真实仓库分支 merge-base 校验（逐个记录退出码）

### A `feature-xuban-presale-expand-opt`

| 仓库 | merge-base --is-ancestor origin/release <branch> 退出码 | origin/release | 分支 commit | merge-base |
|---|---|---|---|---|
| product-server | 0 | a91c18697 | a91c18697 | a91c18697 |
| promotion | 0 | 9b754491d | 9b754491d | 9b754491d |
| promotion-management | 0 | 7102eeb3 | 7102eeb3 | 7102eeb3 |
| student-center | 0 | c25cbd52e | c25cbd52e | c25cbd52e |
| cart | 0 | 3e1e366c | 3e1e366c | 3e1e366c |

（student-data `feature-xuban-presale-expand-opt` = `3e2b681fa`，merge-base = `3e2b681fa`，退出码 0，占位分支）

### B `feature-small-clazz-limit-and-search`

| 仓库 | merge-base --is-ancestor origin/release <branch> 退出码 | origin/release | 分支 commit | merge-base |
|---|---|---|---|---|
| teacher-tool | 0 | 91eb2d45 | 91eb2d45 | 91eb2d45 |
| ces-teach-product | 0 | ecb718524 | ecb718524 | ecb718524 |
| course-center | 0 | 253ed328f | 253ed328f9 | 253ed328f |
| student-center | 0 | c25cbd52e | c25cbd52e | c25cbd52e |

（student-data `feature-small-clazz-limit-and-search` = `3e2b681fa`，merge-base = `3e2b681fa`，退出码 0，占位分支）

> 全部 `merge-base` 即等于各仓库 `origin/release` 头，证明分支无额外提交、干净基于 origin/release。

## 4. A 链接登记确认

`/Users/gaotu/githubDir/quartzZZL/content/高途信息/需求/续班预报名使用膨胀券/links.md` 含 token `Kgphw2GhciYHuvkyy03coeHUnOh`（`grep -c` = 2，分别位于「需求与方案」技术方案（优化）行与「跨会话检索锚点」；`grep` 退出码 0）。