# 飞书文档补录已修复缺陷验证用例（2026-11-19）

## 变更

文档 `EaKXdTkzXoJTStxBJH3cX7Qinzh` 追加新章节「已修复缺陷验证用例（2026-11-19）」。

revision_id 110 → 111。

## 新增章节结构

```
H1: 已修复缺陷验证用例（2026-11-19）
├── H2: 缺陷 A：联报预热收集从计划 activityNumber 时含 null（commit ea1d6f91）
├── H2: 缺陷 B：联报预热合并缓存时读取超出本计划前置课条目（commit 0528c192）
├── H2: 缺陷 C：换课落库 key 不一致——V2 合并页对从计划条目换课不生效（commit f6c12222）
├── H2: 缺陷 D1：换年级合并页对从计划年级无效（commit b61f95a5）
└── H2: 缺陷 D2：换年级未清空从计划条目的换课/勾选记录（commit b61f95a5，连带 f6c12222）
```

## 每条用例覆盖内容

每条用例写明：
- **现象**：缺陷具体表现
- **复现场景**：续班计划号、学员 ID、前置课号、操作步骤
- **修复前表现**：DB 记录或接口返回的错误值
- **修复后结果**：DB 回读值、trace 或对比接口验证结论
- **老链路回归**：老链路不受影响的验证
- **证据**：trace ID / DB row / 归档 commit

## 回读确认

outline fetch 确认 5 个 H2 全部落盘：
- doxcnApvNZ4ilmrsWHRNbKeNafg（缺陷 A）
- doxcnBYON9pzTNYxbR05pvUGzAe（缺陷 B）
- doxcncLY2kZDvtyYT00FXkhS6xe（缺陷 C）
- doxcnefDGwtU7O4f0SF8VUhR9ne（缺陷 D1）
- doxcn0nI3Da8R03X9Ca4RLHlcld（缺陷 D2）
