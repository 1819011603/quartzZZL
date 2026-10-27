---
title: LLM 网关模型映射（redirectToModelCode）
tags: [需求, 参考]
---

# LLM 网关模型映射表（控制面）

## 在哪
- 服务：`baijia.base-tech.ai.llm.litellm`（repo `git.baijia.com/aitech/litellm`，镜像 `acr.baijia.com/uqun/litellm`）
- **映射不是仓库写死**，在**控制面配置**里：
  - 拉取接口：`GET https://tech.baijia.com/llm-gateway/admin/config/all?env=prod|test`（经 baijia-proxy）
  - 代码：`litellm/proxy/common_utils/control_plane_config_manager.py`（`_full_sync` 拉 `/all`）+ `litellm/router.py`（`apply_model_redirect_routing`）
  - 字段：`modelConfigList[].redirectToModelCode`（下线模型 → 接管模型），另有 `deploymentList[].modelParam`（真实上游）
- OSS 另有一份加密运行配置：bucket `tech-ai-project-platform`，object `llm-gateway-config/encrypted_litellm_config_file`

## 映射表（prod、test 一致）
| 下游调用名（modelCode） | redirectToModelCode | 实际上游部署（modelParam） |
|-|-|-|
| `deepseek-v4-flash-0731` | **`deepseek-flash`** | litellm_proxy/deepseek-v4-flash-202605 / deepseek-v4.1-flash |
| `deepseek/DeepSeek-R1-250528` | **`deepseek-flash`** | litellm_proxy/deepseek-v4-flash |
| `doubao/Doubao-1-5-pro-32k` | **`doubao-seed-2-0-lite-260428`** | volcengine/ep-… / sophnet doubao-1-5-pro-32k-250115 |
| `doubao/Doubao-Seed-1-6` | **`doubao-seed-2-0-lite-260428`** | — |
| `deepseek-flash`（目标） | （无） | litellm_proxy/deepseek-v4.1-flash（腾讯/百度） |
| `deepseek-v4.1-flash-1017` | （无） | litellm_proxy/**deepseek/deepseek-flash**（腾讯） |
| `doubao-seed-2-0-lite-260428`（目标） | （无） | 多部署 doubao ep-*（火山/qiniu） |

## 重要含义
1. **网关已自动重定向旧模型**：调 `deepseek-v4-flash-0731` / `deepseek/DeepSeek-R1-250528` → 自动接 `deepseek-flash`；`doubao/Doubao-1-5-pro-32k` / `Doubao-Seed-1-6` → 自动接 `doubao-seed-2-0-lite-260428`。**即：不改 model code 也会走新模型。**
2. 官方「下线替换映射」与控制面一致。
3. ⚠️ 我们显式选的 `deepseek-v4.1-flash-1017` 与网关接管目标 `deepseek-flash` **都是 DeepSeek-V4.1-Flash，但部署不同**（1017 是带日期的具体版本 `deepseek/deepseek-flash`；`deepseek-flash` 走 `deepseek-v4.1-flash`）。若要严格对齐「官方接管值」，应改用 **`deepseek-flash`**。

## 复现
```bash
curl -sk -x http://127.0.0.1:8888 "https://tech.baijia.com/llm-gateway/admin/config/all?env=prod" | \
  python3 -c 'import sys,json;d=json.load(sys.stdin)["data"];[print(m["modelCode"],"→",m.get("redirectToModelCode")) for m in d["modelConfigList"] if m.get("redirectToModelCode")]'
```