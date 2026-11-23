# TEST 可替换场景实际交付（2026-11-23）

## 生效范围

环境为 `test-gtbg-dev-1`，版本 `91012878d692119e79fb7d14baa1bab594c9534d`，镜像 `feature-xuban-dify-offline-91012878-20261123184341`，Pod `student-data-86c8f5db5d-cpwj9`。Apollo `student-data / TEST / application / ai.agent.accessor.override.map` 的最终发布为 `20261123203513-188a49b33afd47c6`。

知识库4项已撤销网关覆盖并恢复Dify：问题建议高中/素养、降退费精品/素养；生产未改。

TEST 当前保留 7 个网关覆盖条目，覆盖 8 类可替换场景（画像与摘要共享一个 agent）：

| 覆盖条目 | 场景 | 最终参数/验证 |
|---|---|---|
| `255107338300556288` | 用户画像、沟通摘要 | `doubao-seed-2-0-lite-260428`；thinking.disabled；复验 `f059219f-2d7c-46c5-945e-fd3a9cdab509.0.3` |
| `256325360053917696` | 服务SOP分析 | `doubao-seed-2-0-lite-260428`；V2 双侧单user 13647 字一致；旧 `315c294d-dbc3-4d8f-adc6-e036ad96d1e1.0.3`、新 `2b757fa1-ac59-4cbd-aac5-1260f6bcba8a.0.3` |
| `262172718139452416` | 分层原因 | `response_format=text`、thinking.disabled；复验 `7a05052d-9094-4a00-aa88-bf44dcf0eb61.0.3` |
| `255743333766281216` | 退费根因 | `deepseek-flash`；旧/新单次请求已取，弱样本结构可用但业务枚举不足；`a32fe4b6-6269-4882-8d39-81c76f8ca23e.0.3` |
| `255733061835044864` | 退费旅程 | `deepseek-flash`；单次、无tools，但模板含既有已解决原因字段差异；`bfd44413-31f5-493d-904b-e670783ff2c4.0.3` |
| `255742622136547328` | 退费课程体验 | `deepseek-flash`；业务正文保留，角色包装差异；`e02d7092-ee55-4e73-b731-b6f31ef2fb6e.0.3` |
| `255743847351465984` | 退费NPS（当前TEST精品模板） | `deepseek-flash`；业务正文保留，精品模板实收；`d2003cc1-b573-4e1c-8918-d3a4d162fe62.0.3` |

## 交付判断

以上是 TEST 的实际网关生效配置和已有入口验证，不是生产发布批准。SOP V2 可按该 fixture 收束为输入一致；画像/摘要/分层指令与业务正文一致但完整 messages 角色包装不同；退费根因、旅程、课程体验、NPS 精品保留正文但有明确包装或模板差异。素养 NPS 无 TEST 旧侧映射，不能列入已替换；见 `../expanded-renewal/nps-suyang-evidence-boundary.md`。

已有的 Dify 恢复 quickTest：降退费 `f558b680-5ab8-461f-9a49-5c29e04fadef.0.3`、素养建议 `3bacf406-b5f0-4034-bef2-55732d412b1f.0.3`，均 `event=message` 且 answer 非空，证明保留项已回到旧链路。

本次没有新增代码、生产配置、生产推理或前端改动；生产后续仍需 DDL、路由、Apollo 发布和逐应用准入。TEST 交付不能外推生产 13 个应用全部通过。
