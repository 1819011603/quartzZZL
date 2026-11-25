# 课节管理（lessonList）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/cronus/lessonList` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 cronus（`/crm/micro-cronus`） |
| epic 路由 | `epic/src/routes.ts`：`/cronus/lessonList`（`microApp: cronus`，`name: 课节管理`，`access: menu_fairy_course`） |
| cronus 路由 | `cronus/config/routes.js`：`/lessonList` → `src/pages/lesson/index.js` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |

## tab 列表

`src/pages/lesson/index.js` 读 URL 参数 `bs`（业务场景，合法值见 `components/BusinessScene/index.js` 的 `businessSceneEnum`；无/非法回退 `default`），另由 `lt`/`type` 决定课节类型（大班课 `normal` / 小灶课 `small`）：

| bs | 中文名 | 组件 | 文档 |
|---|---|---|---|
| `default` | 默认 | `./DefaultLessonList` | [default.md](./default.md) |
| `lessonprepare` | 课前准备 | `./LessonPrepare` | [lessonprepare.md](./lessonprepare.md) |
| `lessonAfter` | 课后督学 | `./LeesonAfter` | [lessonAfter.md](./lessonAfter.md) |
| `emLessonAfter` | 课后督学（EM） | `./EmLessonAfter` | [emLessonAfter.md](./emLessonAfter.md) |
| `prepareRelationLesson` | 关联课节 | `./RelatedLesson` | [prepareRelationLesson.md](./prepareRelationLesson.md) |

> `lessonAfter` 灰度未开而 `emLessonAfter` 已开时，`bs=lessonAfter` 会被改写为 `emLessonAfter`（见 `index.js:127`）。

## 页面级接口（所有 tab 共用）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | `lessonPrepareGrayService` | `/component/student-center/lesson/prepare/gray` | `src/pages/lesson/grayscale/index.js:11` | student-center | `/lesson/prepare/gray` | [POST]/gray [980560] | 课前准备 tab 是否展示 |
| 进页面 | `lessonAfterGrayService` | `/component/student-center/lesson/after/gray` | `src/pages/lesson/grayscale/index.js:25` | student-center | `/lesson/after/gray` | 灰度 [1159240] | 课后督学 tab 是否展示 |
| 进页面 | `relationLessonGrayService` | `/component/student-center/lesson/prepare/relation/gray` | `src/pages/lesson/grayscale/index.js:38` | student-center | `/lesson/prepare/relation/gray` | 关联课节 tab 灰度（复用课前准备灰度字段，额外返回 relationLesson）[4882732] | 关联课节 tab 是否展示 |
| tab 角标（60s 轮询） | `getCount` | `/bgwApi/component/student-center/lesson/prepare/scene/count` | `src/pages/lesson/components/BusinessScene/index.js:100`（service `src/services/lessonPrepare.js:31`） | student-center | `/lesson/prepare/scene/count` | [POST]/scene/count [980553] | 批量取各业务场景 tab 数量角标 |

## 共享组件

> 共享组件（`@/components/TableRender`、`@/components/LessonDetailDrawer`、`@/components/ReportModal`、`@/components/ClazzPeriodSearch`、`@/components/AccountNameFilter`、`@/components/PagerToolTip`、`@gaotu/reach-widget`、`@coeus/render` schema、联邦组件 `mf_iris` 的 `Duanxin`/`AutoStrategyDrawer` 等）另有接口，被多页面复用，待单独归档。

## 短信入口核对（2026-11-25）

源码证据：cronus origin/master `de13f181`；reach-service 本地 master `3675f089f`。源码不等于当前线上部署版本。

| Tab | 短信入口 | anchorCode | reachSceneCode |
|---|---|---|---|
| lessonprepare | BusinessSms；schema.json:702 显示“发短信”，弹窗标题“发催到课短信” | lesson_preparation_before_class | remindAttendClass |
| lessonAfter | LeesonAfter/components/Sms | lesson_supervision_after_class | remindPlayBack / remindExercise |
| emLessonAfter | 复用 LeesonAfter/components/Sms | lesson_supervision_after_class | remindPlayBack / remindExercise |
| default | FormalLesson/index.js:695 → mf_iris/Duanxin；弹窗所有场景由 getReachScene 返回 | lessonData（anchorPoint=1） | 数字场景ID，见下文 |
| prepareRelationLesson | 未在对应目录发现上述 SMS 配置 | 待核实 | 待核实 |

调用链：课前 `/component/student-center/lesson/prepare/operate/validation`、课后 `/component/student-center/lesson/after/operate/validation`，status=1 后调用 `@gaotu/reach-widget` 的 `SMS.show`；传入场景、入口、clazzLessonNumber、subclazzNumber、clazzNumber、title。

模板查询：POST `/bgwApi/reachPortal/sms/getSmsTemplate` → reach-service `ReachServiceSmsController#getSmsTemplate` → `ReachSmsServiceImpl#getSmsTemplate` → `PublishTemplateBizImpl#list`。控制器支持 anchorCode/reachSceneCode 转换为 ID；按登录账号补老师角色。业务层按发布入口、场景与条件匹配发布记录，再过滤启用且未删除的模板；空数组不能直接认定前端渲染故障。

本次反馈班级 `22NL26Q3VM11002`、二讲 dushasha，traceId `cdb30a4f-bcec-4427-b3ad-bea92fb73869.0.0` 尚未核对线上日志。附件两个路径相同，实际仅看到课前“发短信”按钮截图。

测试证据：用户提供的课节 `591524742081732610`、辅导班 `36970315965268736`，请求头 b_client=EES、ingress-traffic-env=test-gtbg-dev-2、traffic-env=test-eco-8。代理当前登录身份，非 dushasha 代课。原数字参数 anchorPoint=1/reachScene=11 返回10条；改为前端代码中的入口/场景 code 后，催到课9条、催回放1条（941）、催练习2条（1493、940），均 code=0。两种入口返回不同，不能把原 curl 当作所有 Tab 的同一请求，也不能用该测试样本证明反馈班级正常。实际服务命中泳道未由日志确认。

待确认：reach-widget 内部请求转换、线上实际 schema/部署版本、反馈班级与老师身份下模板过滤结果。问题2已定位到课前 schema 文案；问题1已沿默认Tab原始trace确认，见下文“默认 Tab 短信发布范围根因”。

## 默认 Tab 短信发布范围根因（2026-11-25）

本次实际入口为默认 Tab → 发短信（不是课后督学 SMS.show）。iris Duanxin 的 Texting 组件将 getSmsTemplate 的 data 原样设置为模板列表；getReachScene(anchorPoint=1) 返回11个场景。

已通过原 trace 及同课节同账号历史请求核实：课节550577198814312459、辅导班34571908035903892、dushasha。课程部门实际为 `10019197/10019736/10019802`（历史部门映射：初中素养/卓越双语），老师PS部门为 `10019197/10019736/10019802/10019849/10019855`，虚拟组织为EM业务线/素养初中学部/教学服务二部/双语成都小班主讲部/六组。信息已成功取到，不是空字段。

生产只读 ACL 查 PublishRecordService#getById 验证：

| 场景 | 发布记录 | 模板 | 策略 | 排除原因 |
|---|---|---|---|---|
| 催回放12 | 366 课节列表大班课催回放 | 1408 课节列表大班课催回放【终】 | 919 工作台催回放 | conditionContent 的 paramConditionType=1（课程部门）仅含26个部门根路径，缺少10019197及本课部门路径；enable=1 |
| 催练习21 | 367 课节列表大班课催练习 | 1410 课节列表大班课催练习【终】 | 921 工作台催练习 | 同一套26部门白名单，同样缺少10019197及本课部门路径；enable=1 |
| 催到课11（对照） | 365 课节列表大班课催到课 | 1403 | 920 工作台催到课 | 筛选的是paramConditionType=11（顾问二讲PS架构），已含10019197/；历史同账号同课节请求成功返回模板1403 |

不能混淆10019198（已配置）与10019197（此次实际所属、未配置）。366、367最后更新时间分别2026-05-09 10:28:05、10:30:20；365为2026-07-08 19:46:05。操作历史已核实，见下文；并非一直未配置。

其他候选也不覆盖此对象：催回放4910仅限10014193/10003833/下两支，4515为编程虚拟组织97353115542003211，其余候选限制其他课程部门/主讲/老师部门；催练习2999为CA财经虚拟组织97353038960303759、2894限制30001130/30000582/30000646、392限制10014193/10006495/10012997及子部门。与当前部门/虚拟组织均不符。原催回放trace及催练习de71075d-a45b-49ed-8d54-bea6a5444451.0.0均明确记录无匹配发布记录并返回code=0,data=[]。

结论：缺的是触达发布记录366、367的课程部门适用范围覆盖，模板本身有ID、发布记录启用，老师和课程信息已获取。若业务要求支持本课程，应由触达配置负责人确定把本课程分支纳入这两条发布范围还是另建专属发布记录；不应直接放开全部部门。此次仅查询，未修改代码或配置。

### 发布范围为何缺失：操作历史核实

只读 `OperateLogService#listByMap({biz_number:366/367,type:3})`，共各3条操作快照：
- 2024-01-31 快照3044/3045：conditionContent=[]。
- 2026-03-25 快照17342/17343：课程部门白名单包含27项，其中含 `10019197/`。
- 2026-05-09 10:28:03，操作账号对应姓名张家望，快照18056（记录366）：白名单变为26项，移除 `10019197/`。
- 2026-05-09 10:30:18，同一操作人，快照18059（记录367）：同样移除 `10019197/`。

两次前后白名单唯一差异是删除10019197/，当前生效记录与5月快照一致。因此更准确的结论是该部门被后续发布范围调整排除，并非新部门一直漏加。其他26个部门仍保留，解释了影响为何集中于这支课程；这里筛选的是课节对应课程部门，不是“二讲角色”或个人是否授权。不能凭本案例断言“绝大部分老师”的覆盖率，若同课程其他老师正常，应核对是否相同课节、相同入口/通道、是否命中特例模板。操作日志仅证明配置变更，未提供删除的业务理由，不能判断误操作还是有意停用。
