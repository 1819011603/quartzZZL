---
title: 续班使用的dify下线 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

---

## 2026-10-27

### 🤖 Claude

- 定为技术优化项（非业务需求），归档名沿用技术项表原名「续班使用的dify下线」
- 最终采用「Apollo 按应用独立切换 + 两阶段（先功能替换、后代码切换）」，替代「直接改 `ai_agent.platform_type`」的一次性做法——因为要能单应用灰度与随时回滚
- 新链路定为复用已上线的 `LlmGatewayAccessor`（caller/场景 `gps-ai`），续班归因已在走该 caller
- 建分支 `feature-xuban-dify-offline`（`--no-track`，起点 `origin/release`）
- 开关落点为新增 `AiAgentPlatformTypeResolver`（Apollo json map `ai.agent.platform.type.override.map`），在 `AiApplicationExecutor` 两处解析处接覆盖——不改库即可单应用切/回滚
- 范围扩到**退费 AI**（prod 共 17 个 Dify 应用：续班 7 + 退费 10），不再只续班
- 试点定为 test `用户画像/沟通摘要-test`（`ai_agent.number=255107338300556288`）
- 试点**双向验证通过**：开关开走网关（`litellm_proxy/...`）、关回 Dify（`message`）——证明「按应用切换 + 可回滚」成立
- 查模型改用 **Dify 控制台 API**（`os.baijia.com/dify/api/console/api/...`，经 baijia-proxy）+ 服务 API `/info` 核归属；得到「agent↔应用↔模型」对应表
- 发现模型不一致：网关走的是默认模型而非原 Dify 模型；且 `doubao*`/`DeepSeek-R1-250528` 不在 gps-ai 可用模型里 → 新增 T-07 处理
- gps-ai **test 加路由** `doubao-seed-2-0-lite-260428`（id 37268）；其余 3 个（Doubao-Seed-1.6 / Doubao-1.5-Pro-32K / DeepSeek-R1(0528)）在网关目录 `status=2` 已下线，加不了同 code，列候选交用户找人确认
- `response_format=json_object`（gps-ai prod DeepSeek 路由 33566，force=false）：**保留**——续班归因靠它稳定 JSON；若退费类迁来共用该 route 且存在纯文本场景，则改为**请求级按应用下发**而非删 route 默认值
- 开关结构定为**按应用的自定义参数**：key `ai.agent.accessor.override.map`，value=`{name, platformType, model, params}`；`name` 必填便于识别 ID；`params` 为任意网关请求参数字段（如 `response_format`）。取代早期只含 platformType 的 `ai.agent.platform.type.override.map`
- 请求侧落地：`AiModelCallOption.extraParams` + `LlmGatewayAccessor` 合并进请求体（`model`/`max_tokens`/`messages` 不可被 params 覆盖）
- 试点按应用配 `model=doubao-seed-2-0-lite-260428` + `params.response_format=json_object` 后实测：`event=litellm_proxy/doubao-seed-2.0-lite`、输出**纯 JSON** → 模型覆盖与自定义参数均生效
- 模型替换以官方【模型下线通知】（火山引擎 2026-09-21）为准：`Doubao-1.5-Pro-32K`/`Doubao-Seed-1.6` → `doubao-seed-2-0-lite-260428`；`DeepSeek-R1-250528`（精品班 3 应用）通知未覆盖，**待定**
- R1/V3 下线通知（建议替换 DeepSeek-V4-Flash）→ 具体采用 `deepseek-v4.1-flash-1017`；gps-ai test 加该路由（id 37270）。至此替换映射**全部确定**
- 退费整条线**统一**迁到 `deepseek-v4.1-flash-1017`（原用 `deepseek-v4-flash-0731` 的素养学部也一并改）——替代「素养用 0731、精品班用 v4.1」的旧口径
- 退费提示词迁移方式定为**原地更新 `prompt_config.core_prompt`**（`updatePromptConfig`，存历史版本、`auto_use_current_version=1` 即生效）；**必须回传原 `afterProcessorPromptConfig`**（「结果JSON格式(...);敏感词过滤」）否则被清空
- 副作用已接受：`core_prompt` 新旧链路共用，过渡期 Dify 侧会看到两份指令；test 直接改，prod 待定「同步切 or 随代码切换」
- 逐应用验证在 test 全通（续班 5 + 退费 6）；`退费NPS` 输出为纯文本、**不带 `params`**（该模型对 `json_object` 返 400）——即「返回格式按应用定」的实例
- 返回格式最终定：**续班(doubao)带 `json_object`；退费(deepseek)一律不带**——实测同模型（deepseek-v4.1）对 `json_object` 行为不稳（课程体验成功、NPS 400），一律去掉靠提示词约束（学生端剥 ``` 围栏）
- prod 待办拆开：T-09 prod Apollo 补 params、T-11 prod 退费提示词迁移、T-12 路由工单审批、T-13 prod 发布、T-14 表状态同步
- **最终采用 `prompt_config.gateway_core_prompt`（新增列）承载新链路提示词**，替代早期「原地改 core_prompt」（会导致 Dify 双指令）与「放 Apollo `prompt`」（Apollo 有值长度限制，27KB 写不进去）。`core_prompt` 保持原样 → 可回退、老链路零变化
- 访问覆盖去掉 `prompt` 字段；`AiApplicationExecutor` 在 `platformType==2` 时读 `gatewayCorePrompt` 覆盖 system 提示词
- 查网关映射：**在控制面**（`tech.baijia.com/llm-gateway/admin/config/all?env=`，字段 `redirectToModelCode`；repo `aitech/litellm`），**不是仓库写死**——旧模型已被自动重定向（0731/R1→`deepseek-flash`；Doubao-1.5/1.6→`doubao-seed-2-0-lite-260428`）
- 退费模型**改为 `deepseek-flash`**（= 官方接管值，取代 `deepseek-v4.1-flash-1017`；两者同为 v4.1 但部署不同）；test 已改并复验（event `litellm_proxy/deepseek-v4.1-flash`）
- **消息结构对齐 Dify 试过、无收益、已回退**（同一应用相似度 0.37/0.55 落在简单结构 0.53 的噪声内）→ 剩余差异主要来自模型随机性+措辞
- **隐藏能力扫描**：全部应用 `tools` 为空、`gt_configs`/敏感词/注释 均关；**唯一功能性隐藏依赖=知识库(dataset)**，仅「生成沟通建议」2 个（已保留 Dify）与【废弃】降退费
- **prod Apollo 置空 `{}` 并发布**（线上全走老链路 Dify）；正式配置（15 应用）等**代码上线后再发**

### 👤 我

- 给出技术项表链接 `https://gaotuedu.feishu.cn/sheets/LvFhsGY7UhTjbWtO7r9c6nkCnbS`（第 10 行）
- 给出迁移表 `https://gaotuedu.feishu.cn/sheets/T9lhsNwL4hzovStIDVDcyy8znRf`，要求新建 tab 并按其他 tab 格式（日期/服务/分支/MR 置前）
- 给出 AI 应用平台链接 `https://os.baijia.com/apps`
- 明确：用 LLM 替换，都用 `https://ai.baijia.com/ai-service/access`、`gps-ai` 这个场景
- 确认：粒度用 `ai_agent`；试点用 `用户画像/沟通摘要-test`；复用现有 `LlmGatewayAccessor`；退费也在范围
- 确认：prod 用官方替换映射；`deepseek-v4-flash-0731` 也统一换成 `deepseek-v4.1-flash-1017`；先弄 test、prod 先别写；17 个迁完都要验证（可 mock）