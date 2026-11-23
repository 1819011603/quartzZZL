# 旧 Dify system prompt 完整复制核对（2026-11-23）

所有者新增要求已按 TEST 范围落实。逐应用核对旧 Dify 来源与新链路承载：

| 场景 | 旧 Dify 来源 | 新链路 TEST 承载 | 结果 |
|---|---|---|---|
| 用户画像 | 旧实收嵌套 system，2272 字 | 代码生成真实 system；TEST 实收 system 2272 字 | 完整正文已复制，当前差异仅旧 flat 单user包装→新 system/user |
| 沟通摘要 | 旧实收嵌套 system，466 字 | 代码生成真实 system；TEST 实收 system 466 字 | 完整正文已复制，当前差异仅角色/包装 |
| 分层 | 旧实收嵌套 system，2715 字 | 代码生成真实 system；TEST 实收 system 2715 字 | 完整正文已复制，当前差异仅角色/包装；text/thinking 参数按已验证修正保留 |
| SOP V2 | 旧 Dify system 与业务内容已整体存在于 flat user；新旧完整 messages 15002 字一致 | 继续保留现有 flat user | 不新增重复 system，避免改变已一致输入 |
| 退费根因 | 生产 Dify pre_prompt 2254 字 | `gateway_core_prompt` 2254 字 | SHA 前16位 `5594013e6fd05d90`，完整相等 |
| 退费旅程 | 生产 Dify pre_prompt 2482 字 | `gateway_core_prompt` 2482 字 | SHA 前16位 `34bef27068183572`，完整相等 |
| 课程体验 | 生产 Dify pre_prompt 2381 字 | `gateway_core_prompt` 2381 字 | SHA 前16位 `b61548f250b16ba1`，完整相等 |
| NPS 精品 | 生产 Dify pre_prompt 473 字 | `gateway_core_prompt` 473 字 | SHA 前16位 `ad64c97078da1d28`，完整相等 |
| NPS 素养副本 | 线上生产 pre_prompt 321 字复制到 TEST Dify 与 TEST `gateway_core_prompt` | Dify app `spcjE2Q2agjjjJ2GYZc_fb2db0ac-d837-43d6-a1ab-8e7b46e06bfa` | SHA256 `792367953211702387ba02b1e2c3a136134fcd753238b134039754c87a920ab4`，双侧实收入口成功 |

完整messages仍可能不同：旧 Dify 将 system 文本包在单个 user 的 flat/伪 JSON 中，新链路使用真实 system+user；这属于消息角色和包装差异，正文未省略或精简。SOP 已完整相等，因此不重复追加 system。

证据：`expanded-scope/full-dify-system-prompt-audit.json`、`expanded-renewal/suyang-nps-copy-validation.md`、既有逐场景 diff 与实收文件。
