# 页面接口知识库

查工单用：**页面地址 → 定位接口 → 定位后端服务/字段**，不用每次人工给接口地址。

## 目录约定

```
知识库/
  README.md                        # 本文件：用法 + 模板
  index.json                       # 机读索引（页面/tab → 接口），供自动检索
  <前端仓库>/
    <页面路由>/
      _page.md                     # 页面级：路由链路、tab 列表、页面级接口
      <tabKey>.md                  # 每个 tab 一个文件（一个页面可多 tab，不混在一起）
```

- 一个页面一个目录；页面级信息放 `_page.md`；**每个 tab 单独一个文件**。
- 命名用前端路由/文件名（如 `clazzRosterOL`），tab 文件用 `tabKey`（如 `continuationService`）。

## 已收录页面

| 页面路由 | 名称 | 仓库 | tab |
|---|---|---|---|
| `/crm/cronus/clazzRosterOL` | 班级花名册 | cronus | default / stageFeedback / refundPrevention / continuationService |
| `/crm/cronus/lessonList` | 课节管理 | cronus | default / lessonprepare / lessonAfter / emLessonAfter / prepareRelationLesson |
| `/crm/cronus/lessonStudentList` | 课节学员 | cronus | default / prepareUser / lessonAfterUser / emLessonAfterUser / prepareRelationLessonUser |
| `/crm/cronus/microLessonStudentList` | 小班课节学员 | cronus | — |
| `/crm/cronus/microClazzManage` | 小班课管理 | cronus | — |
| `/crm/cronus/microClazzRoster` | 小班课花名册 | cronus | default / continuationService |
| `/crm/cronus/onebyOneRoster` | 一对一花名册 | cronus | — |
| `/crm/cronus/examManagement` | 考试管理 | cronus | — |
| `/crm/microFairy/tutoringClassManage` | 辅导班管理 | boss-counselor | — |
| `/ark/app-promotions/continuation-classes` | 续班计划管理（OES，含问卷绑定） | gaotu-fe-promotions | list / renewalProcess |
| `/ark/app-promotions/continuation-classes/pre-register-activity` | 预报名活动 | gaotu-fe-promotions | — |
| `/ark/app-yunfan/newJudgeConfig` | 判单配置 | gaotu_yunfan_fe | judgeOrderConfig / protectionPeriodConfig |
| `/ark/app-yunfan/orderRecall` | 订单可续回溯 | gaotu_yunfan_fe | — |
| `/ark/app-activity/organization` | 组织架构 | boss-activity | — |
| 学员详情页 AI 分析 tab（GAIA 微组件，非独立路由） | AI 分析 / 意向预测 | aianalysisinformations | — |

## tab 文件模板

```md
# <页面> / <tab 中文名>（<tabKey>）

## 定位
| 项 | 值 |
|---|---|
| tab URL | ... |
| 前端仓库 | ... |
| 页面组件 | ... |
| tab 组件 | ... |
| 后端主服务 | ... |

## 接口清单
| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|

## 关键字段（可选）
- ...

## 排查提示
- <症状> → <看哪个接口>

## 青舟接口详情页
- [METHOD /path](url)
```

## 列含义

| 列 | 含义 |
|---|---|
| 触发 | 何时调：进页面 / 筛选 / 翻页 / hover / 点击 / 保存 |
| 前端调用路径 | 前端代码里写的路径（`request('...')`），**不是**后端路径 |
| 前端代码位置 | 该调用所在的文件（排查前端用） |
| 后端服务 | 青舟 appId（= 后端服务名），如 `student-center` |
| 后端 path | 后端 Controller 路径（青舟接口文档里的 path） |
| 接口名 | 青舟接口文档里的中文名 |

## 怎么用（查工单）

1. 拿到页面地址 → 去掉基座前缀，得到 `<仓库>/<页面>/<tabKey>`。
2. 打开对应 tab 文件，看「接口清单」。
3. 或直接读 `index.json`（机读），按页面/接口名/path 检索。
4. 需要字段/入参 → 用青舟 apidoc 查 `interfaceId`（详情页链接已附）。

## 维护方式

- 数据来源：**前端仓库静态代码**（找 `request()` / `@/services/*`）+ **青舟 apidoc**（补后端服务/path/接口名）。
- 前端仓库：`/Users/gaotu/IdeaProjects/WebProject/<repo>`（cronus / epic / boss-counselor…）。
- 前端仓库不知道地址：青舟 `getAllServiceCode` 模糊搜（前端服务多叫 `gaotu-fe-<名>`，`qingzhou_find_service_code` 只做精确匹配会漏），再 `qingzhou_get_service_info` 取 `gitlabUrl` / `gitCloneCmd`（GitLab 未登录也能 clone）。
- 青舟 apidoc CLI：`python3 ~/.claude/skills/qingzhou-apidoc-url/apidoc.py search -i <关键词>`。

## 注意

- 以 `master` 分支代码为准；test 环境可能跑功能分支，接口可能有出入。
- 共享组件（`@/components/*`）的接口被多页面复用，本库只记页面自有/直连的接口，公共组件接口后续单独归档。
- 后端路径由前端 `request` 路径 + 网关路由推导；网关前缀见各服务（如 `component/student-center` → `student-center`）。
