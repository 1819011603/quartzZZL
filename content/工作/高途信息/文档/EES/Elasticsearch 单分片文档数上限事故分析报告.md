https://gaotuedu.feishu.cn/wiki/MGBGw2pdFik0iEk1ZHecM2oXnMb

---

查看当前集群分片id情况
```
GET /_cat/indices?v&h=index,pri,docs.count,docs.deleted,store.size&s=docs.count:desc


GET /_cat/indices?v&h=index,pri,docs.count,docs.deleted,store.size&s=docs.count:desc

```

## 事件概览

  

|   |   |
|---|---|
|项目|内容|
|**事件定级**|事件|
|**涉及服务**|student-data (学员数据服务) / EES|
|**核心索引**|`ads_large_clazz_user_index_v2`|
|**发生时间**|2025-12-05 20:00 ~ 12-06 06:57|
|**持续时长**|约 10 小时 50 分钟|
|**影响范围**|EES 花名册无法显示新报名学员|

  

---

  

## 一、问题描述 (Problem Description)

  

### 1.1 业务现象

  

EES 业务线反馈**"大班课花名册不显示在班学员"**。用户下单后，数据未能正常同步至查询端，导致花名册列表缺失。

  

### 1.2 技术现象

  

后台服务 `student-data` 在消费 MQ 写入 Elasticsearch 时大量报错，导致数据积压。

  

```Plain
┌─────────────────────────────────────────────────────────────┐
│  [MQ Consumer]                                              │
│       │                                                     │
│       ▼                                                     │
│  [Elasticsearch Write] ──── ❌ 大量写入失败 ────            │
│       │                                                     │
│       ▼                                                     │
│  [消息积压] ──── 业务数据无法同步 ──── 花名册缺失           │
└─────────────────────────────────────────────────────────────┘
```

  

---

  

## 二、事故现象与日志 (Symptoms & Logs)

  

### 2.1 业务端报错

  

服务日志中出现大量以下两类异常，表明写入链路已崩溃：

  

#### 异常类型一：存储层拒绝 (Storage Reject)

  

|   |   |
|---|---|
|错误类型|`version_conflict_engine_exception`|
|HTTP 状态码|409 Conflict|
|现象描述|回放 MQ 消息时使用了 `create` 写入，而该文档已经通过 `_reindex` 或之前的写入存在|

**回放消息 导致的异常 回放的时候 已进班的数据 重新insert会报错**

#### 异常类型二：线程池拒绝 (Thread Pool Reject)

  

**写入过快的异常 是以分片为维度的线程池**

|   |   |
|---|---|
|错误类型|`es_rejected_execution_exception`|
|队列容量|10,000|
|实际排队任务|10,003|
|分析|ES 节点写入队列已塞满，由于底层分片无法写入，导致请求堵塞，最终拒绝所有新请求|

  

### 2.2 数据库端异常

  

集群监控显示，索引 `ads_large_clazz_user_index_v2` 的 **Shard 0 停止写入**。通过命令排查发现该分片已达到 Lucene 底层硬限制。

  

**排查命令：**

  

```Bash
GET /ads_large_clazz_user_index_v2/_stats/docs?level=shards
```

  

**关键发现：**

  

|   |   |   |
|---|---|---|
|指标|数值|说明|
|Shard 0 `docs.count`|1,567,031,477|存活文档数（约 15.6 亿）|
|Shard 0 `docs.deleted`|580,452,042|已删除文档数（约 5.8 亿）|
|**总计**|**2,147,483,519**|精确达到 `Integer.MAX_VALUE - 128`|
|其他分片状态|正常|Shard 1-4 未触及上限|

  

> ⚠️ **核心结论**：Shard 0 已完全无法写入任何新数据,无法更新和插入

  

---

  

## 三、技术根因分析 (Root Cause Analysis)

  

### 3.1 核心结论

  

索引 `ads_large_clazz_user_index_v2` 设计为 **5 个主分片**，其中 **Shard 0** 的底层文档总数（存活文档 + 已删除文档）精确达到了 **2,147,483,519**，触发了 **Lucene 的** **`Integer.MAX_VALUE`** **硬上限**，导致该分片彻底"锁死"，无法写入任何新数据。

  

### 3.2 根因推导

  

#### Lucene 单分片限制原理

  

ES 的单分片限制不是指 `count`，而是指**底层 ID 占用**：

  

$$\text{Limit} = \text{Docs Count} + \text{Deleted Docs}$$

  

$$1,567,031,477 + 580,452,042 = \mathbf{2,147,483,519}$$

  

```Plain
┌────────────────────────────────────────────────────────────────┐
│                    Shard 0 容量状态                             │
├────────────────────────────────────────────────────────────────┤
│  ████████████████████████████████████████████████  100%        │
│  │←─── Live Docs: 15.6亿 (73%) ───→│←─ Del: 5.8亿 (27%) ─→│   │
├────────────────────────────────────────────────────────────────┤
│  总占用: 21.47 亿 / 上限: 21.47 亿 = 100% FULL ❌              │
└────────────────────────────────────────────────────────────────┘
```

  

### 3.3 深层原因分析

  

#### 原因一：Nested 类型的文档膨胀效应

  

> **Nested 对象会成倍消耗文档 ID 配额！**

  

在 Elasticsearch 的底层 Lucene 中，Nested（嵌套）对象**并不是存储在主文档内部的**，而是作为**独立的、隐藏的文档**存储的。

  

**计算公式：**

  

$$\text{单条业务数据的实际 Lucene 文档数} = 1 (\text{Root Doc}) + \sum (\text{Nested 数组中的元素个数})$$

  

**举例说明：**

  

假设有一条学生数据（Root Doc），其中：

- `dailyExerciseStatus`（Nested）里有 **3** 条记录
    
- `listenStatus`（Nested）里有 **5** 条记录
    
- `liveAnswerStatus`（Nested）里有 **2** 条记录
    

那么，插入这一条学生数据，底层 Lucene 会实际创建：

  

$$1 + 3 + 5 + 2 = \mathbf{11} \text{ 个文档}$$

  

**当前 Mapping 中的 Nested 字段：**

  

|   |   |   |
|---|---|---|
|Nested 字段名|业务含义|潜在风险|
|`dailyExerciseStatus`|每日练习状态|🟡 中风险：最近30天|
|`examStatus`|考试状态|🟡 中风险：最近30天|
|`intelligentEnglish`|智能英语|🟡 中风险|
|`listenStatus`|听力状态|🟡 中风险|
|`liveAnswerStatus`|直播答题状态|🟡 中风险|
|`offlineExamInfo`|线下考试信息|🟡 中风险：最近30天|
|`summaryExerciseStatus`|总结练习状态|🟡 中风险|

  

> ⚠️ **风险警示**：如果一个学生的 `dailyExerciseStatus` 记录了全年的数据（365条），那么仅仅这一个学生的一条数据，就会在底层消耗 **366 个文档 ID**。这会极快地消耗掉 21 亿的单分片 ID 上限。

![](https://gaotuedu.feishu.cn/space/api/box/stream/download/asynccode/?code=YTI3ODlhM2I4MmE1ODUyMDgyMDU3ZjY3ZTBjYjJlMGJfU3ZVbGZ3VnNRU0RHV3ExUE5qZ2txdEk1QUlRRENTWXlfVG9rZW46TEhMUmJMd2lEb1E2VkR4V0taa2NqZ3VwbjJlXzE3NjYwNDg2NzI6MTc2NjA1MjI3Ml9WNA)

  

  

#### 原因二：Update/Upsert 的文档膨胀机制

  

这是此次事故的**核心痛点**。Lucene 的段文件是**不可变（Immutable）**的，所以无法"原地修改"。

  

**Insert（新增）操作：**

  

|   |   |
|---|---|
|操作描述|写入一条全新数据（ID 不存在）|
|`docs.count` 变化|+1 (+ Nested 子文档数)|
|`docs.deleted` 变化|0|
|ID 占用|占用 1 个 (+ Nested 子文档数) 新 ID|

  

**Update/Upsert（更新）操作：**

  

|   |   |
|---|---|
|操作描述|修改已存在的文档|
|ES 内部流程|① Mark Deleted → ② Insert New|
|`docs.count` 变化|不变（旧的死，新的生）|
|`docs.deleted` 变化|**增加**（旧文档及其所有 Nested 子文档）|
|ID 占用|**翻倍**（Merge 前新旧版本同时占用）|

  

```Plain
┌─────────────────────────────────────────────────────────────┐
│  Update 操作的底层机制                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Step 1: Mark Deleted]                                     │
│  ┌──────────────────┐                                       │
│  │ Old Doc (ID=1001)│ ──→ 标记为 .del (墓碑)                │
│  │ + Nested Doc 1   │ ──→ 标记为 .del                       │
│  │ + Nested Doc 2   │ ──→ 标记为 .del                       │
│  │ + Nested Doc 3   │ ──→ 标记为 .del                       │
│  └──────────────────┘                                       │
│                                                             │
│  [Step 2: Insert New]                                       │
│  ┌──────────────────┐                                       │
│  │ New Doc (ID=1001)│ ──→ 新写入                            │
│  │ + Nested Doc 1'  │ ──→ 新写入                            │
│  │ + Nested Doc 2'  │ ──→ 新写入                            │
│  │ + Nested Doc 3'  │ ──→ 新写入                            │
│  └──────────────────┘                                       │
│                                                             │
│  结果：一次 Update = 4 个 Deleted + 4 个 New = 8 个 ID 槽位  │
└─────────────────────────────────────────────────────────────┘
```

  

**针对 Nested 的 Update 灾难场景：**

  

> 如果你只修改了主文档里的一个普通字段（比如 `age`），**所有的 Nested 子文档也必须全部被标记删除并重新索引**。

  

|   |   |
|---|---|
|场景|某学生有 1000 个 Nested 对象|
|操作|Update 手机号|
|后果 1|ES 必须标记 **1001** 个文档为 Deleted|
|后果 2|重新写入 **1001** 个新文档|
|**总消耗**|**一次小小的更新，消耗了 2002 个 ID 槽位！**|

  

[为什么 Nested 子文档不能复用？](https://gaotuedu.feishu.cn/wiki/IpaYwaS2si7oeFkxeFOcp19un6g)

[Elasticsearch 文档合并与 ID 回收机制详解](https://gaotuedu.feishu.cn/wiki/GtjRwJgufi5SBbkBxo5c6xR2n4b)

#### 为什么 `updateTime` 是“隐形杀手”？ (数据回放时)

### 1.1 结论

  

### Update API（推荐）

  

```Plain
POST /my_index/_update/1
{  "doc": {    "name": "张三"    }}
```

  

|   |   |   |
|---|---|---|
|场景|ES 行为|是否消耗 Doc ID|
|文档内容有变化|删除旧文档 + 写入新文档|✅ 是|
|文档内容无变化（使用 _update API）|跳过写入，直接返回 noop|❌ 否|
|文档内容无变化（使用 index API）|强制重写|✅ 是|

  

后果： 哪怕 `status` 本来就是 1（业务数据没变），但因为 `updateTime` 变了，发给 ES 的 JSON 串和库里存的 JSON 串不一样。

- ES 判定：数据变更。
    
- 动作：标记旧文档（包括所有 Nested 子文档）为 Deleted，写入新文档。
    
- 结果：仅仅为了更新一个时间戳，导致你几十条 Nested 练习记录被重写，消耗几十个 ID。
    

  

### Index API（覆盖写入）

  

```Shell
PUT /my_index/_doc/1
{
  "name": "张三",
  "age": 20
}
```

```Plain
即使内容完全相同，也会重写！       
```

  

### 检查当前写入方式

|   |   |   |
|---|---|---|
|写入方式|代码特征|是否有问题|
|index|esClient.index(doc)|⚠️ 每次都重写|
|update|esClient.update(doc)|✅ 无变化时跳过|
|upsert|update + doc_as_upsert|✅ 无变化时跳过|
|bulk index|bulk.add(indexRequest)|⚠️ 每次都重写|
|bulk update|bulk.add(updateRequest)|✅ 无变化时跳过|

  

  

#### 原因三：架构设计缺陷

  

|   |   |   |
|---|---|---|
|缺陷类型|具体问题|影响|
|**分片预估失误**|900GB 数据 / 仅 5 分片 = 单分片 ~180GB|远超官方建议的 30-50GB|
|**数据倾斜效应**|Shard 0 的 deleted 数是 Shard 1 的 **10 倍**|率先触及上限|
|**缺乏治理策略**|未配置 Rollover 策略|历史数据无限堆积|

  

### 3.4 关键数据证据

  

#### 证据一：极度不均衡的 Deleted Docs 分布

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│           各分片 Deleted Docs 对比                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Shard 0  ████████████████████████████████████  4.06 亿 (基准)  │
│  Shard 1  ████                                  0.38 亿 (9.4%)  │
│  Shard 2  ██████████                            1.08 亿 (26.6%) │
│  Shard 3  ███████                               0.74 亿 (18.2%) │
│  Shard 4  █████                                 0.49 亿 (12.1%) │
│                                                                 │
│  ⚠️ Shard 0 承担的更新/删除压力是 Shard 1 的 10.6 倍！         │
└─────────────────────────────────────────────────────────────────┘
```

  

|   |   |   |
|---|---|---|
|分片|Deleted Docs|相对 Shard 0 占比|
|Shard 0 (Primary)|406,972,088 (约 4.06 亿)|100% (基准)|
|Shard 1 (Primary)|38,416,650 (约 0.38 亿)|9.4%|
|Shard 2 (Primary)|108,601,865 (约 1.08 亿)|26.6%|
|Shard 3 (Primary)|74,535,782 (约 0.74 亿)|18.2%|
|Shard 4 (Primary)|48,852,670 (约 0.49 亿)|12.1%|

  

> 📊 **分析结论**：业务数据在 routing（路由）层面存在严重热点，大量的高频更新数据被集中哈希到了 Shard 0。

  

#### 证据二：容量规划处于"红线区"

  

|   |   |
|---|---|
|统计项|数值|
|总存活文档|78.38 亿|
|总已删除文档|6.77 亿|
|**总文档数**|**85.15 亿**|
|分片数量|5|
|平均单分片负载|85.15 亿 ÷ 5 = **17.03 亿**|
|距上限百分比|17.03 亿 / 21.4 亿 = **79.6%**|

  

```Plain
┌────────────────────────────────────────────────────────────────┐
│                 平均单分片容量水位                              │
├────────────────────────────────────────────────────────────────┤
│  ████████████████████████████████████████░░░░░░░░░░  79.6%     │
│  │←────────── 平均负载: 17.03 亿 ──────────→│← 缓冲 →│         │
│                                                                │
│  ⚠️ 仅剩 20% 缓冲空间，完全不足以应对数据倾斜！               │
│  ⚠️ Shard 0 实际已达 100%，率先爆破                            │
└────────────────────────────────────────────────────────────────┘
```

  

### 3.5 风险总结

  

当前 `ads_large_clazz_user_index` 索引存在的风险因素：

  

|   |   |   |
|---|---|---|
|风险因素|具体表现|危险等级|
|大宽表设计|字段极多，单文档体积大|🔴 高|
|Nested 字段多|7 个 Nested 字段，数组可能很长|🔴 高|
|高频 Upsert|日志证明更新频繁|🔴 高|
|乘法效应|高频更新 × Nested 子文档数 = 指数级 ID 消耗|🔴 极高|

  

  

---

  

![](https://gaotuedu.feishu.cn/space/api/box/stream/download/asynccode/?code=YjAzYWE5ZTYyODM4NTUxZDllZjYyOGMzOWE3NjdlYThfVHJ1WjdPaENneFc3OVNEQkc1Z250cHdLMjN3dnN6b05fVG9rZW46WWNZWWJVT1djbzdyNk54ZTFZTmN2OU13bkJkXzE3NjYwNDg2NzI6MTc2NjA1MjI3Ml9WNA)

![](https://gaotuedu.feishu.cn/space/api/box/stream/download/asynccode/?code=NTIwZWQzMzUyY2FjYjhhYjdhNmMyM2UyMmRiZDg2NDNfY01uTjR4cTlkS21RVDhQelZsWnB3cWVpbXNTN1Uwa1ZfVG9rZW46RmVGNGJacDBZb09nRU14Rk1HeGNvQ3JvbnJkXzE3NjYwNDg2NzI6MTc2NjA1MjI3Ml9WNA)

![](https://gaotuedu.feishu.cn/space/api/box/stream/download/asynccode/?code=N2JkZTQzZDg0MGMxYmRlNjYyOGI3ZGM3M2ZmNzIyN2FfSkdBejlCMGFNb0g1NmdKb1hJMlpwWVdZUUZiWktMWGFfVG9rZW46T010VGJDNjFSb3V3eUJ4M2JrS2NaMjVrbm1mXzE3NjYwNDg2NzI6MTc2NjA1MjI3Ml9WNA)

  

问题原因

**AdsClazzUserLargeStaffOrderedConsumer 组织架构变更 导火索 量大**

**代码bug 导致组织架构重复推送 4号消息堆积超3亿, 5号堆积超7亿 消息 ,诗帅上午上线将消息丢弃**

  

![](https://gaotuedu.feishu.cn/space/api/box/stream/download/asynccode/?code=NmNkYWRhYWQwN2E2ZmQwODFjZjAwY2FmYjRiOTAwOGJfRmtZSk5aQWZuRVNnNzZDUWdScXBXU1pIVXZpS1NQcGJfVG9rZW46Q2xpU2JmcU9kb1hmQlB4Yno2SWMwS2xQbm1FXzE3NjYwNDg2NzI6MTc2NjA1MjI3Ml9WNA)

  

## 四、Nested 类型使用建议

  

### 4.1 建议一：Nested 字段"打平" (Flatten)

  

**适用场景：** Nested 里的字段不需要独立查询（如不需要 `dailyExerciseStatus=Done 且 dailyExerciseTime>10` 的组合查询）

  

|   |   |
|---|---|
|改造前|改造后|
|`"type": "nested"`|`"type": "object"` 或 `keyword` 数组|
|数组 N 个元素 = N+1 个文档|数组 N 个元素 = **1 个文档**|

  

**优点：** 无论数组里有多少元素，都只算 1 个文档

  

### 4.2 建议二：父子文档拆分 (Join Type) —— 慎用

  

**适用场景：** 某些 Nested 数组特别长（如每日打卡，一年 365 条）

  

```Plain
┌──────────────────────────────────────────────────────────────┐
│  改造前：单索引存储                                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ student_index                                           │ │
│  │ ├── 学生基础信息                                         │ │
│  │ └── dailyExerciseStatus (Nested, 365条/年)              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  改造后：拆分为两个索引                                       │
│  ┌────────────────────┐    ┌────────────────────────────┐   │
│  │ student_index      │◄───│ exercise_index             │   │
│  │ ├── student_id     │    │ ├── student_id (关联字段)   │   │
│  │ └── 学生基础信息    │    │ └── 练习记录数据            │   │
│  └────────────────────┘    └────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

  

**优点：**

- 更新学生信息时，**不会**触发练习记录的重写
    
- 新增练习记录时，**不会**导致学生信息重写
    

### 4.3 建议三：减少 Nested 更新频率

  

**痛点：** 现在只要更新 `studentName`，所有 `dailyExerciseStatus` 都要陪葬（重写）

  

**优化方案：**

  

|   |   |   |
|---|---|---|
|方案|描述|效果|
|索引拆分|高频更新字段与静态字段分开存储|最有效|
|Partial Update|使用部分更新 API|有限效果（底层仍是全文档重写）|

  

**拆分示例：**

  

```Plain
┌────────────────────────────────────────────────────────────┐
│  ads_user_basic (低频更新)                                  │
│  ├── student_id                                            │
│  ├── studentName                                           │
│  └── dailyExerciseStatus (Nested 大字段)                   │
├────────────────────────────────────────────────────────────┤
│  ads_user_status (高频更新)                                 │
│  ├── student_id                                            │
│  ├── lastPracticeTime                                      │
│  └── updateTime                                            │
└────────────────────────────────────────────────────────────┘
```

  

### 4.4 建议四：Force Merge 策略

  

由于 Nested 更新会产生海量 Deleted Docs，必须确保集群有足够的空闲时间进行 Merge。

  

|   |   |
|---|---|
|策略|建议|
|避免高峰期 Update|将批量更新任务调度到凌晨低峰期|
|监控 `docs.deleted`|占比超过 20% 时，低峰期触发 `_forcemerge`|
|定期维护|每周固定时间执行 Merge 操作|

  

---

  

## 五、解决方案与恢复 (Resolution)

  

### 5.1 紧急恢复措施

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│                    恢复时间线                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  12-05 20:00   ●──── 故障发生                                   │
│       │                                                         │
│       ▼                                                         │
│  12-05 20:30   ●──── 发现异常，开始排查                         │
│       │                                                         │
│       ▼                                                         │
│  12-05 21:00   ●──── 定位根因：Shard 0 触顶                     │
│       │                                                         │
│       ▼                                                         │
│  12-05 22:00   ●──── 阿里云紧急扩容集群节点                     │
│       │                                                         │
│       ▼                                                         │
│  12-05 23:00   ●──── 创建新索引 v3 (20 分片)                    │
│       │                                                         │
│       ▼                                                         │
│  12-06 00:00   ●──── 开始 Reindex 数据迁移                      │
│       │                                                         │
│       ▼                                                         │
│  12-06 05:30   ●──── Reindex 完成，切换别名                     │
│       │                                                         │
│       ▼                                                         │
│  12-06 06:00   ●──── 开始 MQ 消息回放                           │
│       │                                                         │
│       ▼                                                         │
│  12-06 06:57   ●──── 业务恢复正常 ✅                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

#### 步骤一：集群扩容

  

阿里云紧急增加集群节点，防止在 Reindex 高负载下集群完全宕机。

  

#### 步骤二：重建索引 (Reindex)

  

|   |   |   |
|---|---|---|
|操作项|旧索引 (v2)|新索引 (v3)|
|索引名称|`ads_large_clazz_user_index_v2`|`ads_large_clazz_user_index_v3`|
|分片数量|5|**20** (提升 4 倍)|
|单分片容量|~180GB|~45GB|

  

> ✅ **Reindex 额外收益**：过程会自动剔除 deleted 文档，实现数据"瘦身"

  

#### 步骤三：消息回放 (Replay)

  

**回放配置：**

  

|   |   |
|---|---|
|配置项|值|
|Topic|`student-data_ads_large_clazz_user_ordered_prod`|
|Consumer Group 1|`GID_student-data_ads_large_clazz_user_enterClazz_ordered_prod`|
|Consumer Group 2|`GID_student-data_ads_large_clazz_user_ordered_prod`|
|回放起点|12-05 18:30|

  

**回放范围确定方法：**

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│  如何确定回放范围？                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 查询异常日志，获取受影响的时间范围                           │
│       │                                                         │
│       ▼                                                         │
│  2. 根据 Consumer Group 逐一排查                                │
│       │                                                         │
│       ▼                                                         │
│  3. 获取所有受影响的 groupId 列表                               │
│       │                                                         │
│       ▼                                                         │
│  4. 确定最早异常时间点作为回放起点                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

#### 步骤四：切换流量

  

更改索引别名（Alias）指向 v3，业务恢复写入。

  

```Bash
POST /_aliases
{
  "actions": [
    { "remove": { "index": "ads_large_clazz_user_index_v2", "alias": "ads_large_clazz_user" }},
    { "add":    { "index": "ads_large_clazz_user_index_v3", "alias": "ads_large_clazz_user" }}
  ]
}
```

  

### 5.2 恢复后验证

  

扩容后新索引分片状态：

  

|   |   |   |
|---|---|---|
|指标|数值|说明|
|`docs.count`|4.02 亿|存活文档|
|`docs.deleted`|1.11 亿|墓碑文档|
|当前总占用|5.13 亿|4.02 亿 + 1.11 亿|
|距离上限|**76% 安全空间**|证明扩容策略有效 ✅|

  

---

  

## 六、影响范围 (Impact)

  

|   |   |
|---|---|
|影响维度|具体描述|
|**功能影响**|EES 花名册无法显示新报名学员，影响教务分班与排课查询|
|**用户影响**|工单渠道反馈 12 人（实际受影响数据量级较大）|
|**持续时长**|**10 小时 50 分钟** (20:07 - 06:57)|
|**数据影响**|故障期间新增数据未能同步，需通过消息回放恢复|

  

---

  

## 七、后续整改计划 (Action Items)

  

### 7.1 监控与告警完善（短期）

  

**责任方：** SRE 团队

**截止时间：** 2026.1.31（建议提前）

  

#### 新增监控项

  

**监控命令：**

  

```Bash
GET /<index>/_stats/docs?level=shards
```

  

**告警规则：**

  

|   |   |   |
|---|---|---|
|告警级别|触发条件|处理建议|
|🔴 P1 告警|`(docs.count + docs.deleted) > 18亿`|立即扩容或重建索引|
|🟡 P2 预警|`docs.deleted / docs.count > 30%`|低峰期执行 ForceMerge|
|🟢 P3 通知|`docs.deleted / docs.count > 20%`|关注垃圾数据趋势|

  

### 7.2 架构治理（中期）

  

#### 评估项目

  

|   |   |   |
|---|---|---|
|治理项|目标|预期收益|
|ILM (Rollover) 策略|按数据量（50GB）或条数自动滚动索引|废除"单索引抗所有数据"模式|
|Nested 字段优化|评估打平或拆分可行性|降低 ID 消耗速度|
|分片策略优化|动态调整分片数量|避免单分片过载|

  

  

### 7.3 当前新索引分片当前状态分析

  

|   |   |   |   |
|---|---|---|---|
|指标|Primary|Replica|说明|
|Live Docs|4.07 亿|4.07 亿|一致 ✅|
|Deleted Docs|1.32 亿|1.47 亿|⚠️ 副本更多|
|Deleted 占比|24.50%|26.60%|⚠️ 偏高|
|Generation|712|710|Merge 次数相近|
|距离上限|75%|74%|安全空间充足|

  

#### merge指标计算

|   |   |   |   |
|---|---|---|---|
|指标|计算公式|结果|评估|
|平均每次 Merge 文档数|1699.7亿 / 32.2万|52.8 万/次|正常|
|平均每次 Merge 耗时|45.4天 / 32.2万次|12.2 秒/次|正常|
|Merge 吞吐量|1699.7亿 / 45.4天|4333 万/小时|-|
|限流时间占比|12.4天 / 45.4天|27.20%|⚠️ 严重|
|停止时间占比|3.5天 / 45.4天|7.70%|⚠️ 偏高|

  

当前配置如下

```JSON
"merge": {
          "scheduler": {
            "max_thread_count": "1",    // ⚠️ 只有 1 个 Merge 线程
            "max_merge_count": "1"      // ⚠️ 同时最多 1 个 Merge 任务
          },
          "policy": {
            "floor_segment": "50mb",    // 小于 50MB 的 Segment 视为同层级
            "max_merge_at_once": "5",   // 一次最多合并 5 个 Segment
            "max_merged_segment": "10gb" // 超过 10GB 的 Segment 不参与自动合并
          }
        }
```

  

因为merge性能不足 deleted占比会逐步增加 因为目前deleted占比较高

  

  

### 小幅调整

```Plain
PUT /ads_large_clazz_user_index_v3/_settings
{
  "index": {
    "merge": {
      "scheduler": {
        "max_thread_count": "2",
        "max_merge_count": "4"
      }
    }
  }
}
```

观察 1-2 天，确认：

- 集群 CPU 使用率没有异常飙升
    
- 磁盘 IO 在可接受范围
    
- 限流占比有所下降
    

### 3.2 第二步：继续调整（如果第一步效果好） 将任务数和最大合并segment数提高

  

```Plain
PUT /ads_large_clazz_user_index_v3/_settings
{
  "index": {
    "merge": {
      "scheduler": {
        "max_merge_count": "6"
      },
      "policy": {
        "max_merge_at_once": "10"
      }
    }
  }
}
```

### 3.3 观察指标 deleted占比 cpu 内存使用率

  

## 四、回滚

  

```Plain
# 回滚到原配置（如果需要）
PUT /ads_large_clazz_user_index_v3/_settings
{
  "index": {
      "merge" : {
          "scheduler" : {
            "max_thread_count" : "1",
            "max_merge_count" : "1"
          },
          "policy" : {
            "floor_segment" : "50mb",
            "max_merge_at_once" : "5",
            "max_merged_segment" : "10gb"
          }
        }
  }
}
```

  

  

  

## 八、附录 (Appendix)

  

### 8.1 故障现场数据快照

  

**Shard 0 爆满证据：**

  

```JSON
// GET /ads_large_clazz_user_index_v2/_stats
{
  "total": {
    "docs": {
      "count": 15676127892,
      "deleted": 2526305881
    }
  },
  "shards": {
    "0": [
      {
        "routing": { "primary": true, "node": "sykIf69..." },
        "docs": {
          "count": 1567031477, 
          "deleted": 580452042  // Sum = 2,147,483,519 (MAX_VALUE)
        }
      }
    ]
  }
}
```

  

**扩容后状态验证：**

  

```JSON
// GET /ads_large_clazz_user_index_v3/_stats/docs?level=shards
{
  "routing": { 
    "state": "STARTED", 
    "primary": true,
    "node": "cdiPOLI..." 
  },
  "docs": {
    "count": 402766855,   // 存活：4.02亿
    "deleted": 111214673  // 墓碑：1.11亿
  }
  // 当前总占用 = 5.13亿，距离上限 21.4亿 还有 76% 安全空间 ✅
}
```

  

### 8.2 故障原理图解

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│                    故障传播链路                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [业务写入]                                                      │
│       │                                                         │
│       ▼                                                         │
│  [MQ Topic]                                                     │
│       │                                                         │
│       ▼                                                         │
│  [Consumer] ─────────────────────────────────────┐              │
│       │                                          │              │
│       ▼                                          │              │
│  [Elasticsearch]                                 │              │
│       │                                          │              │
│       ▼                                          │              │
│  ┌─────────────────────────────────────────┐    │              │
│  │ Index: ads_large_clazz_user_index_v2    │    │              │
│  ├─────────────────────────────────────────┤    │              │
│  │ Shard 0 (Primary)                       │    │              │
│  │ ┌─────────────────────────────────────┐ │    │              │
│  │ │ 状态: 21.47亿/21.47亿 = 100% FULL  │ │    │              │
│  │ │ Live Docs:  15.6 亿                 │ │    │              │
│  │ │ Dead Docs:  5.8 亿                  │ │    │              │
│  │ └─────────────────────────────────────┘ │    │              │
│  │                  💥                      │    │              │
│  │          无法分配新 Doc ID              │    │              │
│  │          拒绝写入 → 抛出异常            │    │              │
│  └─────────────────────────────────────────┘    │              │
│                    │                             │              │
│                    ▼                             │              │
│            [返回 Rejected / 409]                 │              │
│                    │                             │              │
│                    ▼                             │              │
│            [Consumer 重试] ◄─────────────────────┘              │
│                    │                                            │
│                    ▼                                            │
│            [集群线程池爆满]                                      │
│                    │                                            │
│                    ▼                                            │
│            [全链路雪崩] 💥💥💥                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

### 8.3 各分片完整状态数据

  

|   |   |   |   |   |   |
|---|---|---|---|---|---|
|分片|类型|docs.count|docs.deleted|总占用|占上限比例|
|Shard 0|Primary|1,567,031,477|406,972,088|1,974,003,565|91.9%|
|Shard 1|Primary|1,568,117,654|38,416,650|1,606,534,304|74.8%|
|Shard 2|Primary|1,567,662,778|108,601,865|1,676,264,643|78.1%|
|Shard 3|Primary|1,567,958,178|74,535,782|1,642,493,960|76.5%|
|Shard 4|Primary|1,567,293,859|48,852,670|1,616,146,529|75.3%|

  

### 8.4 关键命令速查

  

```Bash
# 查看索引分片级别文档统计
GET /ads_large_clazz_user_index_v2/_stats/docs?level=shards

# 查看集群健康状态
GET /_cluster/health?level=indices

# 执行强制合并（低峰期）
POST /ads_large_clazz_user_index_v3/_forcemerge?max_num_segments=1

# 查看待处理的任务
GET /_cat/pending_tasks?v

# 查看线程池状态
GET /_cat/thread_pool?v&h=node_name,name,active,queue,rejected
```

  

---

  

## 九、经验教训总结

  

### 9.1 技术层面

  

|   |   |
|---|---|
|教训|改进措施|
|低估了 Nested 类型的 ID 消耗|使用前必须评估数组长度和更新频率|
|分片数量规划不足|按官方建议 30-50GB/分片设计，预留 50% 缓冲|
|缺少分片级别监控|新增 `docs.count + docs.deleted` 阈值告警|
|未考虑 Update 的副作用|高频更新场景避免使用 Nested 类型|

  

### 9.2 流程层面

  

|   |   |
|---|---|
|教训|改进措施|
|索引设计缺乏评审|新索引上线前必须进行容量评估|
|缺乏定期巡检|每月检查核心索引的分片健康状态|
|告警覆盖不全|补充底层存储指标的监控告警|

  

---

附录:

旧索引分片的文档数据

```JSON
{
  "_shards" : {
    "total" : 10,
    "successful" : 9,
    "failed" : 0
  },
  "_all" : {
    "primaries" : {
      "docs" : {
        "count" : 7838063946,
        "deleted" : 677379055
      }
    },
    "total" : {
      "docs" : {
        "count" : 14109096415,
        "deleted" : 1105267852
      }
    }
  },
  "indices" : {
    "ads_large_clazz_user_index_v2" : {
      "uuid" : "Ev0EHbKhR1OY7Q94i6Utig",
      "primaries" : {
        "docs" : {
          "count" : 7838063946,
          "deleted" : 677379055
        }
      },
      "total" : {
        "docs" : {
          "count" : 14109096415,
          "deleted" : 1105267852
        }
      },
      "shards" : {
        "0" : [
          {
            "docs" : {
              "count" : 1567031477,
              "deleted" : 406972088
            },
            "commit" : {
              "id" : "mNC8QAOPYVgmGR8SOrAo4A==",
              "generation" : 36716,
              "user_data" : {
                "local_checkpoint" : "2419211974",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "2419211975",
                "translog_uuid" : "VHsRujlAQsW48CgqXLIDvQ",
                "history_uuid" : "ji_VBPgQSU-KjbiTbJf0wg",
                "max_seq_no" : "2419211974"
              },
              "num_docs" : 1567031477
            },
            "seq_no" : {
              "max_seq_no" : 2419211974,
              "local_checkpoint" : 2419211974,
              "global_checkpoint" : 2419211974
            },
            "retention_leases" : {
              "primary_term" : 8,
              "version" : 1909560,
              "leases" : [
                {
                  "id" : "peer_recovery/sykIf69-Qa6ihEXUA4x4GA",
                  "retaining_seq_no" : 2419211975,
                  "timestamp" : 1764952522994,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/Gk7BYl9vSDet_ygorbQKRA",
                  "retaining_seq_no" : 2419211975,
                  "timestamp" : 1764992740828,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg352.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg352.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "1" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "Gk7BYl9vSDet_ygorbQKRA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 1568117654,
              "deleted" : 52420100
            },
            "commit" : {
              "id" : "1i0DWAxm9bHWQMVUHTBDFA==",
              "generation" : 36651,
              "user_data" : {
                "local_checkpoint" : "2336421496",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "2336421497",
                "translog_uuid" : "mYiKGZrQRpezcWo0yFjeXw",
                "history_uuid" : "k4_-xQ_cTmG_H9-zqyWwdw",
                "max_seq_no" : "2336421496"
              },
              "num_docs" : 1568117654
            },
            "seq_no" : {
              "max_seq_no" : 2336421496,
              "local_checkpoint" : 2336421496,
              "global_checkpoint" : 2336421496
            },
            "retention_leases" : {
              "primary_term" : 8,
              "version" : 1912288,
              "leases" : [
                {
                  "id" : "peer_recovery/Gk7BYl9vSDet_ygorbQKRA",
                  "retaining_seq_no" : 2336421497,
                  "timestamp" : 1764969606790,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sykIf69-Qa6ihEXUA4x4GA",
                  "retaining_seq_no" : 2336421497,
                  "timestamp" : 1764992740763,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg350.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg350.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "sykIf69-Qa6ihEXUA4x4GA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 1568117654,
              "deleted" : 38416650
            },
            "commit" : {
              "id" : "mNC8QAOPYVgmGR8SOrAo4Q==",
              "generation" : 36067,
              "user_data" : {
                "local_checkpoint" : "2336421496",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "2336421497",
                "translog_uuid" : "FEpOklSsRMmjSTfd2k05jw",
                "history_uuid" : "k4_-xQ_cTmG_H9-zqyWwdw",
                "max_seq_no" : "2336421496"
              },
              "num_docs" : 1568117654
            },
            "seq_no" : {
              "max_seq_no" : 2336421496,
              "local_checkpoint" : 2336421496,
              "global_checkpoint" : 2336421496
            },
            "retention_leases" : {
              "primary_term" : 8,
              "version" : 1912288,
              "leases" : [
                {
                  "id" : "peer_recovery/Gk7BYl9vSDet_ygorbQKRA",
                  "retaining_seq_no" : 2336421497,
                  "timestamp" : 1764969606790,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sykIf69-Qa6ihEXUA4x4GA",
                  "retaining_seq_no" : 2336421497,
                  "timestamp" : 1764992740763,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg352.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg352.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "2" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "Mq1GaPRHRbeEwRYQv53sXw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 1567662778,
              "deleted" : 108601865
            },
            "commit" : {
              "id" : "JDMMf1m4AnlK4AXNxrbPww==",
              "generation" : 35610,
              "user_data" : {
                "local_checkpoint" : "2282932457",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "2282932458",
                "translog_uuid" : "IwfkKyfJQ1eSnpvYY59p-w",
                "history_uuid" : "KKGD9PioRXOZKG8Bl5EI1Q",
                "max_seq_no" : "2282932457"
              },
              "num_docs" : 1567662778
            },
            "seq_no" : {
              "max_seq_no" : 2282932457,
              "local_checkpoint" : 2282932457,
              "global_checkpoint" : 2282932457
            },
            "retention_leases" : {
              "primary_term" : 7,
              "version" : 1912021,
              "leases" : [
                {
                  "id" : "peer_recovery/Mq1GaPRHRbeEwRYQv53sXw",
                  "retaining_seq_no" : 2282932458,
                  "timestamp" : 1764969558348,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/tWqoCtLIRoaXlfl2KgjBuA",
                  "retaining_seq_no" : 2282932458,
                  "timestamp" : 1764992740766,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg34y.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg34y.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "tWqoCtLIRoaXlfl2KgjBuA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 1567662778,
              "deleted" : 106046847
            },
            "commit" : {
              "id" : "u7w6xoBgE/QCb2zBJwSSZw==",
              "generation" : 36150,
              "user_data" : {
                "local_checkpoint" : "2282932457",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "2282932458",
                "translog_uuid" : "__kdLDJ_QGS2X17pruTy9g",
                "history_uuid" : "KKGD9PioRXOZKG8Bl5EI1Q",
                "max_seq_no" : "2282932457"
              },
              "num_docs" : 1567662778
            },
            "seq_no" : {
              "max_seq_no" : 2282932457,
              "local_checkpoint" : 2282932457,
              "global_checkpoint" : 2282932457
            },
            "retention_leases" : {
              "primary_term" : 7,
              "version" : 1912021,
              "leases" : [
                {
                  "id" : "peer_recovery/Mq1GaPRHRbeEwRYQv53sXw",
                  "retaining_seq_no" : 2282932458,
                  "timestamp" : 1764969558348,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/tWqoCtLIRoaXlfl2KgjBuA",
                  "retaining_seq_no" : 2282932458,
                  "timestamp" : 1764992740766,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg34z.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg34z.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "3" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "tWqoCtLIRoaXlfl2KgjBuA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 1567958178,
              "deleted" : 74535782
            },
            "commit" : {
              "id" : "u7w6xoBgE/QCb2zBJwSSZg==",
              "generation" : 35818,
              "user_data" : {
                "local_checkpoint" : "2240416202",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "2240416203",
                "translog_uuid" : "vMqtJsLkTU-15Kq3jziDGQ",
                "history_uuid" : "leSeU-xKQBivvhrJImTIYg",
                "max_seq_no" : "2240416202"
              },
              "num_docs" : 1567958178
            },
            "seq_no" : {
              "max_seq_no" : 2240416202,
              "local_checkpoint" : 2240416202,
              "global_checkpoint" : 2240416202
            },
            "retention_leases" : {
              "primary_term" : 6,
              "version" : 1911891,
              "leases" : [
                {
                  "id" : "peer_recovery/ZN1eXXaPSC2O7JKB7za_Ag",
                  "retaining_seq_no" : 2240416203,
                  "timestamp" : 1764969590766,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/tWqoCtLIRoaXlfl2KgjBuA",
                  "retaining_seq_no" : 2240416203,
                  "timestamp" : 1764992740710,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg34z.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg34z.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "ZN1eXXaPSC2O7JKB7za_Ag",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 1567958178,
              "deleted" : 51492586
            },
            "commit" : {
              "id" : "uzNTiyZILLKnV2r9N34Oiw==",
              "generation" : 35214,
              "user_data" : {
                "local_checkpoint" : "2240416202",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "2240416203",
                "translog_uuid" : "56lnmj43SoqdshfX4KC_xw",
                "history_uuid" : "leSeU-xKQBivvhrJImTIYg",
                "max_seq_no" : "2240416202"
              },
              "num_docs" : 1567958178
            },
            "seq_no" : {
              "max_seq_no" : 2240416202,
              "local_checkpoint" : 2240416202,
              "global_checkpoint" : 2240416202
            },
            "retention_leases" : {
              "primary_term" : 6,
              "version" : 1911891,
              "leases" : [
                {
                  "id" : "peer_recovery/ZN1eXXaPSC2O7JKB7za_Ag",
                  "retaining_seq_no" : 2240416203,
                  "timestamp" : 1764969590766,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/tWqoCtLIRoaXlfl2KgjBuA",
                  "retaining_seq_no" : 2240416203,
                  "timestamp" : 1764992740710,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg351.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg351.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "4" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "Mq1GaPRHRbeEwRYQv53sXw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 1567293859,
              "deleted" : 48852670
            },
            "commit" : {
              "id" : "JDMMf1m4AnlK4AXNxrbPyg==",
              "generation" : 35092,
              "user_data" : {
                "local_checkpoint" : "2210431034",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "2210431035",
                "translog_uuid" : "LTe793vhQ12PocXBLn5eQg",
                "history_uuid" : "b3RNO1-oRMGSRSGlvuLfCA",
                "max_seq_no" : "2210431034"
              },
              "num_docs" : 1567293859
            },
            "seq_no" : {
              "max_seq_no" : 2210431034,
              "local_checkpoint" : 2210431034,
              "global_checkpoint" : 2210431034
            },
            "retention_leases" : {
              "primary_term" : 7,
              "version" : 1910875,
              "leases" : [
                {
                  "id" : "peer_recovery/ZN1eXXaPSC2O7JKB7za_Ag",
                  "retaining_seq_no" : 2210431035,
                  "timestamp" : 1764969590766,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/Mq1GaPRHRbeEwRYQv53sXw",
                  "retaining_seq_no" : 2210431035,
                  "timestamp" : 1764992740710,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg34y.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg34y.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "ZN1eXXaPSC2O7JKB7za_Ag",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 1567293859,
              "deleted" : 217929264
            },
            "commit" : {
              "id" : "uzNTiyZILLKnV2r9N34OjA==",
              "generation" : 35087,
              "user_data" : {
                "local_checkpoint" : "2210431034",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "2210431035",
                "translog_uuid" : "S_agS8KKQ5u6d6wOV6kUsQ",
                "history_uuid" : "b3RNO1-oRMGSRSGlvuLfCA",
                "max_seq_no" : "2210431034"
              },
              "num_docs" : 1567293859
            },
            "seq_no" : {
              "max_seq_no" : 2210431034,
              "local_checkpoint" : 2210431034,
              "global_checkpoint" : 2210431034
            },
            "retention_leases" : {
              "primary_term" : 7,
              "version" : 1910875,
              "leases" : [
                {
                  "id" : "peer_recovery/ZN1eXXaPSC2O7JKB7za_Ag",
                  "retaining_seq_no" : 2210431035,
                  "timestamp" : 1764969590766,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/Mq1GaPRHRbeEwRYQv53sXw",
                  "retaining_seq_no" : 2210431035,
                  "timestamp" : 1764992740710,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg351.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze9jmflv7qqxbugg351.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ]
      }
    }
  }
}
```

  

  

新索引分片的文档数据

```JSON
{
  "_shards" : {
    "total" : 40,
    "successful" : 40,
    "failed" : 0
  },
  "_all" : {
    "primaries" : {
      "docs" : {
        "count" : 8123709620,
        "deleted" : 2918441609
      }
    },
    "total" : {
      "docs" : {
        "count" : 16247417203,
        "deleted" : 5989826395
      }
    }
  },
  "indices" : {
    "ads_large_clazz_user_index_v3" : {
      "uuid" : "RI7qQVWXRgy7ji0foCU1-A",
      "primaries" : {
        "docs" : {
          "count" : 8123709620,
          "deleted" : 2918441609
        }
      },
      "total" : {
        "docs" : {
          "count" : 16247417203,
          "deleted" : 5989826395
        }
      },
      "shards" : {
        "0" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "cdiPOLI1StG7ZEE3USHmkQ",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406593215,
              "deleted" : 132476534
            },
            "commit" : {
              "id" : "UhpVlyAQPT2WJXNtgrA7VA==",
              "generation" : 712,
              "user_data" : {
                "local_checkpoint" : "50486334",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50409635",
                "translog_uuid" : "eAJqfLmaQJyppj4NVamIzA",
                "history_uuid" : "CekimltJQfWbYN6ELHAfhg",
                "max_seq_no" : "50486351"
              },
              "num_docs" : 406524344
            },
            "seq_no" : {
              "max_seq_no" : 50505805,
              "local_checkpoint" : 50505805,
              "global_checkpoint" : 50505805
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69866,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 50505736,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50505736,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "-aPLbDvAShiRKKpCKh2MiA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406593231,
              "deleted" : 148007021
            },
            "commit" : {
              "id" : "z704A36pUAXQcAqpjogTyA==",
              "generation" : 710,
              "user_data" : {
                "local_checkpoint" : "50499910",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50441061",
                "translog_uuid" : "1DAhLWhuQK-bP_6iE_heww",
                "history_uuid" : "CekimltJQfWbYN6ELHAfhg",
                "max_seq_no" : "50499962"
              },
              "num_docs" : 406571726
            },
            "seq_no" : {
              "max_seq_no" : 50505805,
              "local_checkpoint" : 50505805,
              "global_checkpoint" : 50505805
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69866,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 50505736,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50505736,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "1" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "-aPLbDvAShiRKKpCKh2MiA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 405981413,
              "deleted" : 143739549
            },
            "commit" : {
              "id" : "z704A36pUAXQcAqpjod3PQ==",
              "generation" : 698,
              "user_data" : {
                "local_checkpoint" : "50277788",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50272371",
                "translog_uuid" : "nhKkiuAaSmGsgAlKHkptDw",
                "history_uuid" : "9BIxoimUQfC-_zKkz93wrQ",
                "max_seq_no" : "50277791"
              },
              "num_docs" : 405905629
            },
            "seq_no" : {
              "max_seq_no" : 50299639,
              "local_checkpoint" : 50299639,
              "global_checkpoint" : 50299639
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69733,
              "leases" : [
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50299571,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 50299571,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "5kbBEJXcSuOgC_fc0V9o9A",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 405981146,
              "deleted" : 184753564
            },
            "commit" : {
              "id" : "hrI4PrWPALR7Jm1COlGoqg==",
              "generation" : 708,
              "user_data" : {
                "local_checkpoint" : "50277392",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50274082",
                "translog_uuid" : "XWRa83sJS_epAi0YaBArmQ",
                "history_uuid" : "9BIxoimUQfC-_zKkz93wrQ",
                "max_seq_no" : "50277392"
              },
              "num_docs" : 405904411
            },
            "seq_no" : {
              "max_seq_no" : 50299639,
              "local_checkpoint" : 50299639,
              "global_checkpoint" : 50299639
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69733,
              "leases" : [
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50299571,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 50299571,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "2" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "5kbBEJXcSuOgC_fc0V9o9A",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406432554,
              "deleted" : 120880267
            },
            "commit" : {
              "id" : "hrI4PrWPALR7Jm1COlIzxw==",
              "generation" : 710,
              "user_data" : {
                "local_checkpoint" : "50375477",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50313848",
                "translog_uuid" : "eO_atTXKRUm5Bpb7OlsHmw",
                "history_uuid" : "SsL2drbqQnWncom_XI_GLA",
                "max_seq_no" : "50375484"
              },
              "num_docs" : 406399743
            },
            "seq_no" : {
              "max_seq_no" : 50387088,
              "local_checkpoint" : 50387088,
              "global_checkpoint" : 50387088
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69718,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 50387030,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 50387030,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "sX43Fh2iSGmcqODm85DZzg",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406432909,
              "deleted" : 120692265
            },
            "commit" : {
              "id" : "X8E4NAQLZSDbVftT4yLLlQ==",
              "generation" : 707,
              "user_data" : {
                "local_checkpoint" : "50364161",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50283846",
                "translog_uuid" : "uv4Lq6xoQnSV74SJczTw3w",
                "history_uuid" : "SsL2drbqQnWncom_XI_GLA",
                "max_seq_no" : "50364163"
              },
              "num_docs" : 406357432
            },
            "seq_no" : {
              "max_seq_no" : 50387088,
              "local_checkpoint" : 50387088,
              "global_checkpoint" : 50387088
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69718,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 50387030,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 50387030,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "3" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "5kbBEJXcSuOgC_fc0V9o9A",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406133715,
              "deleted" : 161364078
            },
            "commit" : {
              "id" : "hrI4PrWPALR7Jm1COlHSXw==",
              "generation" : 702,
              "user_data" : {
                "local_checkpoint" : "50314269",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50238758",
                "translog_uuid" : "fYiwpa2uRf2FmtHP3VRPcQ",
                "history_uuid" : "sF0A35WTROWzhhgQpT66hQ",
                "max_seq_no" : "50314285"
              },
              "num_docs" : 406068460
            },
            "seq_no" : {
              "max_seq_no" : 50335043,
              "local_checkpoint" : 50335043,
              "global_checkpoint" : 50335043
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69963,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 50335040,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 50335040,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "PLAQqVOoSheNheBvxeyLNw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406133715,
              "deleted" : 190955656
            },
            "commit" : {
              "id" : "qHfkfvHqg7rBCXG9NhutUg==",
              "generation" : 707,
              "user_data" : {
                "local_checkpoint" : "50311320",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50248711",
                "translog_uuid" : "PiwSfKFcRn-NB027wJ8K6A",
                "history_uuid" : "sF0A35WTROWzhhgQpT66hQ",
                "max_seq_no" : "50311320"
              },
              "num_docs" : 406055407
            },
            "seq_no" : {
              "max_seq_no" : 50335043,
              "local_checkpoint" : 50335043,
              "global_checkpoint" : 50335043
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69963,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 50335040,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 50335040,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "4" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "-aPLbDvAShiRKKpCKh2MiA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406168570,
              "deleted" : 165582269
            },
            "commit" : {
              "id" : "z704A36pUAXQcAqpjodv8g==",
              "generation" : 707,
              "user_data" : {
                "local_checkpoint" : "50182206",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50108403",
                "translog_uuid" : "N8muFOdIQ_WYiyzgkCVyhw",
                "history_uuid" : "GVAU3-wmTbiROZ9cYDCd7w",
                "max_seq_no" : "50182207"
              },
              "num_docs" : 406087236
            },
            "seq_no" : {
              "max_seq_no" : 50203972,
              "local_checkpoint" : 50203972,
              "global_checkpoint" : 50203972
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69650,
              "leases" : [
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50203914,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 50203914,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "sX43Fh2iSGmcqODm85DZzg",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406168700,
              "deleted" : 157856181
            },
            "commit" : {
              "id" : "X8E4NAQLZSDbVftT4yNTNA==",
              "generation" : 711,
              "user_data" : {
                "local_checkpoint" : "50194820",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50135350",
                "translog_uuid" : "ExJwlGwhTFqZjAnMnfMf2A",
                "history_uuid" : "GVAU3-wmTbiROZ9cYDCd7w",
                "max_seq_no" : "50195123"
              },
              "num_docs" : 406135222
            },
            "seq_no" : {
              "max_seq_no" : 50203972,
              "local_checkpoint" : 50203972,
              "global_checkpoint" : 50203972
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69650,
              "leases" : [
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50203914,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 50203914,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "5" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "cdiPOLI1StG7ZEE3USHmkQ",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406255740,
              "deleted" : 131059349
            },
            "commit" : {
              "id" : "UhpVlyAQPT2WJXNtgrCnVQ==",
              "generation" : 698,
              "user_data" : {
                "local_checkpoint" : "50264056",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50196165",
                "translog_uuid" : "aK-Kt6QURju9K_JLxbDI5A",
                "history_uuid" : "1v17NEXmRAaf9n2hQxodkA",
                "max_seq_no" : "50264057"
              },
              "num_docs" : 406208617
            },
            "seq_no" : {
              "max_seq_no" : 50274846,
              "local_checkpoint" : 50274846,
              "global_checkpoint" : 50274846
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69628,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 50274793,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50274793,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "-aPLbDvAShiRKKpCKh2MiA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406255708,
              "deleted" : 165375696
            },
            "commit" : {
              "id" : "z704A36pUAXQcAqpjog0EA==",
              "generation" : 703,
              "user_data" : {
                "local_checkpoint" : "50274067",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50220071",
                "translog_uuid" : "jSq6sKkcQs-o3eSRZHWBng",
                "history_uuid" : "1v17NEXmRAaf9n2hQxodkA",
                "max_seq_no" : "50274435"
              },
              "num_docs" : 406254021
            },
            "seq_no" : {
              "max_seq_no" : 50274846,
              "local_checkpoint" : 50274846,
              "global_checkpoint" : 50274846
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69628,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 50274793,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50274793,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "6" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "cdiPOLI1StG7ZEE3USHmkQ",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406175513,
              "deleted" : 156620332
            },
            "commit" : {
              "id" : "UhpVlyAQPT2WJXNtgrATJw==",
              "generation" : 714,
              "user_data" : {
                "local_checkpoint" : "50178102",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50130173",
                "translog_uuid" : "oz4rQvNzQv-XM1rKiU8_Sw",
                "history_uuid" : "JntjIrfxS8imoiMRq_7GqQ",
                "max_seq_no" : "50178421"
              },
              "num_docs" : 406087905
            },
            "seq_no" : {
              "max_seq_no" : 50222996,
              "local_checkpoint" : 50222996,
              "global_checkpoint" : 50222996
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69571,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 50222991,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 50222991,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "PLAQqVOoSheNheBvxeyLNw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406175496,
              "deleted" : 139888925
            },
            "commit" : {
              "id" : "qHfkfvHqg7rBCXG9NhuuIA==",
              "generation" : 704,
              "user_data" : {
                "local_checkpoint" : "50201357",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50130173",
                "translog_uuid" : "U4er9SsaSUSYVbzxmlgz0g",
                "history_uuid" : "JntjIrfxS8imoiMRq_7GqQ",
                "max_seq_no" : "50201425"
              },
              "num_docs" : 406092620
            },
            "seq_no" : {
              "max_seq_no" : 50222996,
              "local_checkpoint" : 50222996,
              "global_checkpoint" : 50222996
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69571,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 50222991,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 50222991,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "7" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "-aPLbDvAShiRKKpCKh2MiA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406405658,
              "deleted" : 114700553
            },
            "commit" : {
              "id" : "z704A36pUAXQcAqpjoexJQ==",
              "generation" : 702,
              "user_data" : {
                "local_checkpoint" : "50192160",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50121113",
                "translog_uuid" : "4E7K-3UTRY-JZvUh6hPrkg",
                "history_uuid" : "lBuIjm-BTCKS5i980H5B9A",
                "max_seq_no" : "50192168"
              },
              "num_docs" : 406355407
            },
            "seq_no" : {
              "max_seq_no" : 50209986,
              "local_checkpoint" : 50209986,
              "global_checkpoint" : 50209986
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69667,
              "leases" : [
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50209930,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 50209930,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "sX43Fh2iSGmcqODm85DZzg",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406405907,
              "deleted" : 178990453
            },
            "commit" : {
              "id" : "X8E4NAQLZSDbVftT4yNI+w==",
              "generation" : 705,
              "user_data" : {
                "local_checkpoint" : "50199800",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50138481",
                "translog_uuid" : "Ea3F9PhpS2-8D6vihf62eA",
                "history_uuid" : "lBuIjm-BTCKS5i980H5B9A",
                "max_seq_no" : "50199837"
              },
              "num_docs" : 406373176
            },
            "seq_no" : {
              "max_seq_no" : 50209986,
              "local_checkpoint" : 50209986,
              "global_checkpoint" : 50209986
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69667,
              "leases" : [
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50209930,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 50209930,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "8" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "-aPLbDvAShiRKKpCKh2MiA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406015038,
              "deleted" : 139963954
            },
            "commit" : {
              "id" : "z704A36pUAXQcAqpjofGRw==",
              "generation" : 697,
              "user_data" : {
                "local_checkpoint" : "50173612",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50102661",
                "translog_uuid" : "EJ6DD41WRemHdC6snCN2oQ",
                "history_uuid" : "jJpd82P0Qrm1VoAEuPnbBA",
                "max_seq_no" : "50173745"
              },
              "num_docs" : 405975697
            },
            "seq_no" : {
              "max_seq_no" : 50189868,
              "local_checkpoint" : 50189868,
              "global_checkpoint" : 50189868
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69628,
              "leases" : [
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50189797,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 50189797,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "sX43Fh2iSGmcqODm85DZzg",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406015053,
              "deleted" : 137164694
            },
            "commit" : {
              "id" : "X8E4NAQLZSDbVftT4yNYDQ==",
              "generation" : 699,
              "user_data" : {
                "local_checkpoint" : "50180979",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "50117870",
                "translog_uuid" : "j-H6MDBURZae27iUEl2ZJA",
                "history_uuid" : "jJpd82P0Qrm1VoAEuPnbBA",
                "max_seq_no" : "50181006"
              },
              "num_docs" : 405986551
            },
            "seq_no" : {
              "max_seq_no" : 50189868,
              "local_checkpoint" : 50189868,
              "global_checkpoint" : 50189868
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69628,
              "leases" : [
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 50189797,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 50189797,
                  "timestamp" : 1766022588729,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "9" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "5kbBEJXcSuOgC_fc0V9o9A",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406013154,
              "deleted" : 148152184
            },
            "commit" : {
              "id" : "hrI4PrWPALR7Jm1COlGcLQ==",
              "generation" : 693,
              "user_data" : {
                "local_checkpoint" : "49972653",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49926716",
                "translog_uuid" : "wXsGlrqjR3C7XdEtPzby6Q",
                "history_uuid" : "m7mJPanzSi29MnT4DekdEw",
                "max_seq_no" : "49973156"
              },
              "num_docs" : 405915755
            },
            "seq_no" : {
              "max_seq_no" : 50018831,
              "local_checkpoint" : 50018831,
              "global_checkpoint" : 50018831
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69709,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 50018828,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 50018828,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "PLAQqVOoSheNheBvxeyLNw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406013154,
              "deleted" : 146638947
            },
            "commit" : {
              "id" : "qHfkfvHqg7rBCXG9NhxSbg==",
              "generation" : 698,
              "user_data" : {
                "local_checkpoint" : "50010569",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49951379",
                "translog_uuid" : "gEzXL7EDQ1e15Z9ndza2Fg",
                "history_uuid" : "m7mJPanzSi29MnT4DekdEw",
                "max_seq_no" : "50010639"
              },
              "num_docs" : 405980622
            },
            "seq_no" : {
              "max_seq_no" : 50018831,
              "local_checkpoint" : 50018831,
              "global_checkpoint" : 50018831
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69709,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 50018828,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 50018828,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "10" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "5kbBEJXcSuOgC_fc0V9o9A",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406322776,
              "deleted" : 138196679
            },
            "commit" : {
              "id" : "hrI4PrWPALR7Jm1COlJiKQ==",
              "generation" : 696,
              "user_data" : {
                "local_checkpoint" : "49840972",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49780116",
                "translog_uuid" : "hnr90VnHTJC8S_8IN61X3Q",
                "history_uuid" : "3FrhWuDWS-OUL8NBRHnWNQ",
                "max_seq_no" : "49840988"
              },
              "num_docs" : 406303500
            },
            "seq_no" : {
              "max_seq_no" : 49845190,
              "local_checkpoint" : 49845190,
              "global_checkpoint" : 49845190
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69668,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49845187,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49845187,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "PLAQqVOoSheNheBvxeyLNw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406322792,
              "deleted" : 113406810
            },
            "commit" : {
              "id" : "qHfkfvHqg7rBCXG9NhwVvw==",
              "generation" : 692,
              "user_data" : {
                "local_checkpoint" : "49831248",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49761324",
                "translog_uuid" : "F3QXcSzERBuVHNma2ifGPQ",
                "history_uuid" : "3FrhWuDWS-OUL8NBRHnWNQ",
                "max_seq_no" : "49831271"
              },
              "num_docs" : 406284117
            },
            "seq_no" : {
              "max_seq_no" : 49845190,
              "local_checkpoint" : 49845190,
              "global_checkpoint" : 49845190
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69668,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49845187,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49845187,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "11" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "cdiPOLI1StG7ZEE3USHmkQ",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406157313,
              "deleted" : 183653965
            },
            "commit" : {
              "id" : "UhpVlyAQPT2WJXNtgrAURg==",
              "generation" : 700,
              "user_data" : {
                "local_checkpoint" : "49789897",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49707712",
                "translog_uuid" : "c_-HLBKoQ2K8fJ7cKXE82g",
                "history_uuid" : "WqMS4mZhTQaAldC3CI90gg",
                "max_seq_no" : "49790866"
              },
              "num_docs" : 406074149
            },
            "seq_no" : {
              "max_seq_no" : 49832832,
              "local_checkpoint" : 49832832,
              "global_checkpoint" : 49832832
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69645,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49832830,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49832830,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "PLAQqVOoSheNheBvxeyLNw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406157464,
              "deleted" : 162609383
            },
            "commit" : {
              "id" : "qHfkfvHqg7rBCXG9NhxBig==",
              "generation" : 699,
              "user_data" : {
                "local_checkpoint" : "49822582",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49811306",
                "translog_uuid" : "1ccLeFUKQw2BtopLpKFTGw",
                "history_uuid" : "WqMS4mZhTQaAldC3CI90gg",
                "max_seq_no" : "49822589"
              },
              "num_docs" : 406127199
            },
            "seq_no" : {
              "max_seq_no" : 49832832,
              "local_checkpoint" : 49832832,
              "global_checkpoint" : 49832832
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69645,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49832830,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49832830,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "12" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "5kbBEJXcSuOgC_fc0V9o9A",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 405563469,
              "deleted" : 166670543
            },
            "commit" : {
              "id" : "hrI4PrWPALR7Jm1COlHWtg==",
              "generation" : 709,
              "user_data" : {
                "local_checkpoint" : "49798132",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49793547",
                "translog_uuid" : "Z7vzuVNhQ3CyNuDh9tgkyw",
                "history_uuid" : "POmPLORmSNmvH9iYyx23Zw",
                "max_seq_no" : "49798137"
              },
              "num_docs" : 405491033
            },
            "seq_no" : {
              "max_seq_no" : 49816600,
              "local_checkpoint" : 49816600,
              "global_checkpoint" : 49816600
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69770,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49816547,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 49816547,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "sX43Fh2iSGmcqODm85DZzg",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 405563668,
              "deleted" : 163579061
            },
            "commit" : {
              "id" : "X8E4NAQLZSDbVftT4yNHBQ==",
              "generation" : 703,
              "user_data" : {
                "local_checkpoint" : "49806277",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49741784",
                "translog_uuid" : "ekbUpYwuRxmgzdTW_t1TcA",
                "history_uuid" : "POmPLORmSNmvH9iYyx23Zw",
                "max_seq_no" : "49806404"
              },
              "num_docs" : 405522438
            },
            "seq_no" : {
              "max_seq_no" : 49816600,
              "local_checkpoint" : 49816600,
              "global_checkpoint" : 49816600
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69770,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49816547,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 49816547,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "13" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "5kbBEJXcSuOgC_fc0V9o9A",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406263069,
              "deleted" : 151726057
            },
            "commit" : {
              "id" : "hrI4PrWPALR7Jm1COlJxfw==",
              "generation" : 694,
              "user_data" : {
                "local_checkpoint" : "49836334",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49818175",
                "translog_uuid" : "kmOnEfzEQLepHfPmwgeOYg",
                "history_uuid" : "WO0jnhrAQMSqmfa8a3Nj1A",
                "max_seq_no" : "49836337"
              },
              "num_docs" : 406256378
            },
            "seq_no" : {
              "max_seq_no" : 49838140,
              "local_checkpoint" : 49838140,
              "global_checkpoint" : 49838140
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69787,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49838138,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49838138,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "PLAQqVOoSheNheBvxeyLNw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406263069,
              "deleted" : 137888993
            },
            "commit" : {
              "id" : "qHfkfvHqg7rBCXG9Nhx6ow==",
              "generation" : 697,
              "user_data" : {
                "local_checkpoint" : "49834985",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49780291",
                "translog_uuid" : "RRp1h7J0Sx65NIuHjv0RXg",
                "history_uuid" : "WO0jnhrAQMSqmfa8a3Nj1A",
                "max_seq_no" : "49835084"
              },
              "num_docs" : 406248816
            },
            "seq_no" : {
              "max_seq_no" : 49838140,
              "local_checkpoint" : 49838140,
              "global_checkpoint" : 49838140
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69787,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49838138,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49838138,
                  "timestamp" : 1766022612578,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "14" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "cdiPOLI1StG7ZEE3USHmkQ",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406601764,
              "deleted" : 117266903
            },
            "commit" : {
              "id" : "UhpVlyAQPT2WJXNtgrDBCg==",
              "generation" : 706,
              "user_data" : {
                "local_checkpoint" : "49799228",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49737525",
                "translog_uuid" : "IyMnGcFfQricq_rM9Dd2WA",
                "history_uuid" : "DbjbyPrlTVWqeh7VFu2NCQ",
                "max_seq_no" : "49799267"
              },
              "num_docs" : 406570685
            },
            "seq_no" : {
              "max_seq_no" : 49806790,
              "local_checkpoint" : 49806790,
              "global_checkpoint" : 49806790
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69743,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49806787,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49806787,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "PLAQqVOoSheNheBvxeyLNw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406601764,
              "deleted" : 143819947
            },
            "commit" : {
              "id" : "qHfkfvHqg7rBCXG9NhubSA==",
              "generation" : 709,
              "user_data" : {
                "local_checkpoint" : "49762635",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49715942",
                "translog_uuid" : "MSJLOVpCSjSbOv_0Ragsmw",
                "history_uuid" : "DbjbyPrlTVWqeh7VFu2NCQ",
                "max_seq_no" : "49762810"
              },
              "num_docs" : 406514171
            },
            "seq_no" : {
              "max_seq_no" : 49806790,
              "local_checkpoint" : 49806790,
              "global_checkpoint" : 49806790
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69743,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49806787,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49806787,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "15" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "cdiPOLI1StG7ZEE3USHmkQ",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406298295,
              "deleted" : 187070125
            },
            "commit" : {
              "id" : "UhpVlyAQPT2WJXNtgrAfVA==",
              "generation" : 700,
              "user_data" : {
                "local_checkpoint" : "49773271",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49695411",
                "translog_uuid" : "9ZkwFLOKQGWEtfpUgJ_jhQ",
                "history_uuid" : "v8NuN7d-R1OC4hXhQnvsmA",
                "max_seq_no" : "49773271"
              },
              "num_docs" : 406213856
            },
            "seq_no" : {
              "max_seq_no" : 49796839,
              "local_checkpoint" : 49796839,
              "global_checkpoint" : 49796839
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69673,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49796785,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 49796785,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "-aPLbDvAShiRKKpCKh2MiA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406298375,
              "deleted" : 182375058
            },
            "commit" : {
              "id" : "z704A36pUAXQcAqpjodw4Q==",
              "generation" : 706,
              "user_data" : {
                "local_checkpoint" : "49773212",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49693797",
                "translog_uuid" : "gk1AGrMvQFirrjOpED2cpQ",
                "history_uuid" : "v8NuN7d-R1OC4hXhQnvsmA",
                "max_seq_no" : "49773242"
              },
              "num_docs" : 406213545
            },
            "seq_no" : {
              "max_seq_no" : 49796839,
              "local_checkpoint" : 49796839,
              "global_checkpoint" : 49796839
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69673,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49796785,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 49796785,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "16" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "cdiPOLI1StG7ZEE3USHmkQ",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406093920,
              "deleted" : 183689416
            },
            "commit" : {
              "id" : "UhpVlyAQPT2WJXNtgrCfHg==",
              "generation" : 708,
              "user_data" : {
                "local_checkpoint" : "49644617",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49618991",
                "translog_uuid" : "xLhIQbd5QpCI9Js3IRuigA",
                "history_uuid" : "iFHCVB-cTkGHE2SMAajDOg",
                "max_seq_no" : "49644650"
              },
              "num_docs" : 406052498
            },
            "seq_no" : {
              "max_seq_no" : 49656089,
              "local_checkpoint" : 49656089,
              "global_checkpoint" : 49656089
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69668,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49656087,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49656087,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "PLAQqVOoSheNheBvxeyLNw",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406094155,
              "deleted" : 134496650
            },
            "commit" : {
              "id" : "qHfkfvHqg7rBCXG9Nhuk4w==",
              "generation" : 705,
              "user_data" : {
                "local_checkpoint" : "49629370",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49551228",
                "translog_uuid" : "HJipI82qQO-RKg5zb8gekQ",
                "history_uuid" : "iFHCVB-cTkGHE2SMAajDOg",
                "max_seq_no" : "49629433"
              },
              "num_docs" : 406006967
            },
            "seq_no" : {
              "max_seq_no" : 49656089,
              "local_checkpoint" : 49656089,
              "global_checkpoint" : 49656089
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69668,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49656087,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/PLAQqVOoSheNheBvxeyLNw",
                  "retaining_seq_no" : 49656087,
                  "timestamp" : 1766022613967,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj8.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "17" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "5kbBEJXcSuOgC_fc0V9o9A",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 405941465,
              "deleted" : 137450443
            },
            "commit" : {
              "id" : "hrI4PrWPALR7Jm1COlIkEA==",
              "generation" : 701,
              "user_data" : {
                "local_checkpoint" : "49785839",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49736379",
                "translog_uuid" : "gJMA97zNSE6cMPERDsSaxQ",
                "history_uuid" : "tj5O_G1KQACFInJxpKbXiQ",
                "max_seq_no" : "49785845"
              },
              "num_docs" : 405909019
            },
            "seq_no" : {
              "max_seq_no" : 49798745,
              "local_checkpoint" : 49798745,
              "global_checkpoint" : 49798745
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69645,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49798685,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 49798685,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "sX43Fh2iSGmcqODm85DZzg",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 405942303,
              "deleted" : 153018656
            },
            "commit" : {
              "id" : "X8E4NAQLZSDbVftT4yM4fg==",
              "generation" : 693,
              "user_data" : {
                "local_checkpoint" : "49785914",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49725090",
                "translog_uuid" : "VRks1iSAQn-HaoE379fbDA",
                "history_uuid" : "tj5O_G1KQACFInJxpKbXiQ",
                "max_seq_no" : "49786071"
              },
              "num_docs" : 405909171
            },
            "seq_no" : {
              "max_seq_no" : 49798745,
              "local_checkpoint" : 49798745,
              "global_checkpoint" : 49798745
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69645,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49798685,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 49798685,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "18" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "5kbBEJXcSuOgC_fc0V9o9A",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406420841,
              "deleted" : 141401702
            },
            "commit" : {
              "id" : "hrI4PrWPALR7Jm1COlH3pw==",
              "generation" : 717,
              "user_data" : {
                "local_checkpoint" : "49746565",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49677637",
                "translog_uuid" : "NgHUK6pvQKO9ZL9yZ1qiJA",
                "history_uuid" : "ehbyCSlOTqi0CYvDuUUPjQ",
                "max_seq_no" : "49746582"
              },
              "num_docs" : 406369384
            },
            "seq_no" : {
              "max_seq_no" : 49764234,
              "local_checkpoint" : 49764234,
              "global_checkpoint" : 49764234
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69635,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49764166,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 49764166,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmja.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "sX43Fh2iSGmcqODm85DZzg",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 406421091,
              "deleted" : 152292681
            },
            "commit" : {
              "id" : "X8E4NAQLZSDbVftT4yK40g==",
              "generation" : 705,
              "user_data" : {
                "local_checkpoint" : "49740331",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49713474",
                "translog_uuid" : "s88tAM3MSdyTGcM0jK4rBg",
                "history_uuid" : "ehbyCSlOTqi0CYvDuUUPjQ",
                "max_seq_no" : "49740331"
              },
              "num_docs" : 406338939
            },
            "seq_no" : {
              "max_seq_no" : 49764234,
              "local_checkpoint" : 49764234,
              "global_checkpoint" : 49764234
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69635,
              "leases" : [
                {
                  "id" : "peer_recovery/5kbBEJXcSuOgC_fc0V9o9A",
                  "retaining_seq_no" : 49764166,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/sX43Fh2iSGmcqODm85DZzg",
                  "retaining_seq_no" : 49764166,
                  "timestamp" : 1766022594270,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj6.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ],
        "19" : [
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : true,
              "node" : "cdiPOLI1StG7ZEE3USHmkQ",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 405870127,
              "deleted" : 134012710
            },
            "commit" : {
              "id" : "UhpVlyAQPT2WJXNtgrATkw==",
              "generation" : 689,
              "user_data" : {
                "local_checkpoint" : "49441841",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49394143",
                "translog_uuid" : "gcSmLkTGTVeA5DTSZv_xeA",
                "history_uuid" : "lg-3uooQRhSxn8kRniPkyg",
                "max_seq_no" : "49442608"
              },
              "num_docs" : 405779212
            },
            "seq_no" : {
              "max_seq_no" : 49487070,
              "local_checkpoint" : 49487070,
              "global_checkpoint" : 49487070
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69482,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49487027,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 49487027,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj7.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          },
          {
            "routing" : {
              "state" : "STARTED",
              "primary" : false,
              "node" : "-aPLbDvAShiRKKpCKh2MiA",
              "relocating_node" : null
            },
            "docs" : {
              "count" : 405869894,
              "deleted" : 120338142
            },
            "commit" : {
              "id" : "z704A36pUAXQcAqpjogrng==",
              "generation" : 694,
              "user_data" : {
                "local_checkpoint" : "49485185",
                "max_unsafe_auto_id_timestamp" : "-1",
                "min_retained_seq_no" : "49435229",
                "translog_uuid" : "NDEFE_6VQRiJ6Ib5nmVopw",
                "history_uuid" : "lg-3uooQRhSxn8kRniPkyg",
                "max_seq_no" : "49485194"
              },
              "num_docs" : 405860863
            },
            "seq_no" : {
              "max_seq_no" : 49487070,
              "local_checkpoint" : 49487070,
              "global_checkpoint" : 49487070
            },
            "retention_leases" : {
              "primary_term" : 1,
              "version" : 69482,
              "leases" : [
                {
                  "id" : "peer_recovery/cdiPOLI1StG7ZEE3USHmkQ",
                  "retaining_seq_no" : 49487027,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                },
                {
                  "id" : "peer_recovery/-aPLbDvAShiRKKpCKh2MiA",
                  "retaining_seq_no" : 49487027,
                  "timestamp" : 1766022600346,
                  "source" : "peer recovery"
                }
              ]
            },
            "shard_path" : {
              "state_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "data_path" : "/ssd/1/hippo_slave/sys_carbon_5_es-cn-4xl3gu6ls0007l185_es_worker_i-2ze92z31oo2buqhffmj9.worker_12_63/es_worker_process/data/nodes/0",
              "is_custom_data_path" : false
            }
          }
        ]
      }
    }
  }
}
```

  

  

merge数据 执行增加线程前

```JSON
{
  "_shards" : {
    "total" : 40,
    "successful" : 40,
    "failed" : 0
  },
  "_all" : {
    "primaries" : {
      "merges" : {
        "current" : 2,
        "current_docs" : 18466246,
        "current_size_in_bytes" : 1659375893,
        "total" : 322151,
        "total_time_in_millis" : 3925683964,
        "total_docs" : 169974255460,
        "total_size_in_bytes" : 14003302545697,
        "total_stopped_time_in_millis" : 299088335,
        "total_throttled_time_in_millis" : 1067150410,
        "total_auto_throttle_in_bytes" : 106287475
      }
    },
    "total" : {
      "merges" : {
        "current" : 2,
        "current_docs" : 18466246,
        "current_size_in_bytes" : 1659375893,
        "total" : 612790,
        "total_time_in_millis" : 7266225366,
        "total_docs" : 311436132775,
        "total_size_in_bytes" : 24066285414406,
        "total_stopped_time_in_millis" : 345985132,
        "total_throttled_time_in_millis" : 2091381546,
        "total_auto_throttle_in_bytes" : 211145075
      }
    }
  },
  "indices" : {
    "ads_large_clazz_user_index_v3" : {
      "uuid" : "RI7qQVWXRgy7ji0foCU1-A",
      "primaries" : {
        "merges" : {
          "current" : 2,
          "current_docs" : 18466246,
          "current_size_in_bytes" : 1659375893,
          "total" : 322151,
          "total_time_in_millis" : 3925683964,
          "total_docs" : 169974255460,
          "total_size_in_bytes" : 14003302545697,
          "total_stopped_time_in_millis" : 299088335,
          "total_throttled_time_in_millis" : 1067150410,
          "total_auto_throttle_in_bytes" : 106287475
        }
      },
      "total" : {
        "merges" : {
          "current" : 2,
          "current_docs" : 18466246,
          "current_size_in_bytes" : 1659375893,
          "total" : 612790,
          "total_time_in_millis" : 7266225366,
          "total_docs" : 311436132775,
          "total_size_in_bytes" : 24066285414406,
          "total_stopped_time_in_millis" : 345985132,
          "total_throttled_time_in_millis" : 2091381546,
          "total_auto_throttle_in_bytes" : 211145075
        }
      }
    }
  }
}
```

  

  

执行增加merge线程前 的delete count数 12.18-11:29:00 执行

GET /ads_large_clazz_user_index_v3/_stats/merge,docs?filter_path=indices.*.primaries

```JSON
{
  "indices" : {
    "ads_large_clazz_user_index_v3" : {
      "primaries" : {
        "docs" : {
          "count" : 8125220756,
          "deleted" : 2935734965
        },
        "merges" : {
          "current" : 0,
          "current_docs" : 0,
          "current_size_in_bytes" : 0,
          "total" : 323583,
          "total_time_in_millis" : 3931807412,
          "total_docs" : 170480518505,
          "total_size_in_bytes" : 14029265152541,
          "total_stopped_time_in_millis" : 299088335,
          "total_throttled_time_in_millis" : 1068066551,
          "total_auto_throttle_in_bytes" : 105334225
        }
      }
    }
  }
}
```

  

  

Segment 大小

GET /_cat/segments/ads_large_clazz_user_index_v3?v&h=shard,prirep,segment,docs.count,docs.deleted,size&s=size:desc&size=20

```Shell
shard prirep segment docs.count docs.deleted     size
0     r      _1bf0    102068003      2479295   11.4gb
8     p      _r59      95051941     13934627   11.4gb
16    p      _14gn    101673951      3935525   11.3gb
5     r      _1l6l     84123120      6613961   11.3gb
0     p      _1cn0     98191180      3597664   11.3gb
8     r      _1e6x    108254717      4954011   11.3gb
13    r      _13a9     94915488     12547946   11.2gb
4     r      _16nu     77384589     26742459   11.2gb
1     p      _1brc     98775371     13888609   11.2gb
9     r      _rgc      93685314     17396353   11.2gb
7     p      _tt6     104473278     18082164   11.1gb
10    r      _17ca    104960036      9495892   11.1gb
18    p      _wte      98340224     18618906   11.1gb
2     p      _tm8      89611525     25746696   11.1gb
14    r      _tcm     101933211     14764599   11.1gb
10    p      _14un     96367549     15267453   11.1gb
14    p      _1aac    108803915      5544156   11.1gb
7     r      _sqo      88203299     24824842   11.1gb
11    p      _r38      92495185     24832619   11.1gb
19    r      _qgu     108524668     12262021     11gb
9     p      _rtf     106555170     15576537     11gb
6     r      _12eq    100610466      9737439     11gb
5     p      _1au5     98929150     16260532     11gb
19    p      _rto     101673259     14626828   10.9gb
16    r      _ewt      59784470     32187714   10.9gb
6     p      _12q6    100740634     11136086   10.9gb
15    p      _v0g      98564638     18541995   10.8gb
19    p      _1ad8     97232981     18602507   10.8gb
0     p      _10in     95053212     24862192   10.8gb
1     r      _o0z      86907721     30301876   10.8gb
4     r      _svk     101800986     21218115   10.8gb
1     p      _po1      92069914     26852986   10.8gb
13    p      _10vk    111594637     11511212   10.7gb
16    p      _f3g      65134466     29764863   10.7gb
11    r      _jxm      94725392     26420023   10.7gb
19    r      _16aj     96352360     21812176   10.7gb
7     p      _1gfl    102027448     11128700   10.7gb
4     p      _12wf     82545295     21325951   10.7gb
14    r      _1frp    108819486      7860280   10.7gb
11    p      _igz      89189985     27520672   10.6gb
2     p      _1rm8    114507041      5155481   10.6gb
4     p      _qtc      87069068     25118551   10.6gb
8     r      _xrx      95564486     19564585   10.6gb
2     r      _p0i      87538393     20977764   10.6gb
3     r      _raf      86373428     29525267   10.6gb
1     r      _fuc      73198323     30893764   10.6gb
13    r      _iwq      76717743     25401756   10.6gb
10    r      _fzo      79795477     37966086   10.5gb
3     p      _gkc      73556545     29844075   10.5gb
17    r      _dka      61846803     45386362   10.5gb
5     p      _wc1     106076306     17472825   10.5gb
6     r      _e4h      56725553     39115930   10.5gb
16    r      _1avg     69780174     18088240   10.4gb
17    p      _jsb      95071936     32016786   10.4gb
3     p      _pbn      90963673     26929391   10.4gb
13    p      _rue      60127784     17219434   10.4gb
17    p      _roe      85651869     31981323   10.4gb
9     r      _18p6    105741510     18152701   10.3gb
4     p      _gtw      91777901     34991405   10.3gb
8     p      _gxj      97708997     35296281   10.3gb
14    p      _gyi      93785999     33281204   10.3gb
15    p      _hqn      93862228     31312557   10.3gb
2     p      _m8p     104905465     28767820   10.3gb
7     r      _f69      53225577     39972170   10.3gb
5     p      _gvt      85630802     33459201   10.3gb
18    r      _sjt     101687143     15531739   10.3gb
17    p      _1f4p     99341550     12523023   10.2gb
12    r      _fnu      89724900     35388380   10.2gb
9     r      _g6a      86520425     36215321   10.2gb
9     p      _fgr      82601034     35782274   10.2gb
10    p      _ef5      73234775     39922564   10.2gb
18    p      _18ie     95995614     29272080   10.2gb
18    r      _e64      91789781     35196292   10.2gb
13    p      _fex      88360095     32655194   10.2gb
17    r      _15j1     91381343     13306596   10.2gb
15    r      _ddl      50912441     53072558   10.2gb
4     p      _dn0      48649599     40818222   10.2gb
2     r      _hum      99977195     34004345   10.2gb
3     r      _ffz      55934105     47952348   10.2gb
7     r      _l1m     103281702     27592103   10.2gb
3     r      _joa      94216939     28937942   10.2gb
4     r      _eda      49825927     48459875   10.2gb
8     p      _dww      52007559     42044436   10.1gb
8     r      _enb      50600334     44485589   10.1gb
5     r      _dlh      46530211     57441641   10.1gb
15    r      _iq5      96472149     28616220   10.1gb
6     p      _iqo      97756995     27762906   10.1gb
18    p      _hl6      84468364     28729299   10.1gb
7     p      _p3b      94996992     20332983   10.1gb
14    r      _fus      91033733     31932143     10gb
11    r      _fjb      80913112     34473142     10gb
11    r      _vfn      71503590     31673178     10gb
18    r      _15kq     88318566     11752231     10gb
5     r      _j39      94515625     28237367    9.9gb
4     r      _ice      84672947     28818675    9.9gb
12    p      _isz      94646106     37106099    9.9gb
11    p      _dvq      72079351     41884831    9.9gb
19    p      _h7n      96350062     37524336    9.9gb
18    r      _2yo      37889985     23284428    9.9gb
18    p      _2yo      37889985     23284428    9.9gb
16    r      _325      38338693     24197754    9.8gb
16    p      _325      38338693     24197754    9.8gb
10    p      _vdo     118822193     13149182    9.8gb
0     p      _3rv      45126957     44817482    9.8gb
0     r      _3rv      45126957     44817482    9.8gb
11    r      _3iu      43786926     41264283    9.8gb
11    p      _3iu      43786926     41264283    9.8gb
14    r      _335      37980356     32261579    9.8gb
14    p      _335      37980356     32261579    9.8gb
15    p      _3oa      44852031     36762857    9.8gb
15    r      _3oa      44852113     36762775    9.8gb
4     p      _346      37934251     21974931    9.8gb
4     r      _346      37934251     21974931    9.8gb
13    r      _3de      34918462     28844187    9.8gb
1     p      _3q3      45931459     41399981    9.8gb
1     r      _3q3      45931459     41399981    9.8gb
18    r      _3ap      41768444     36811812    9.8gb
18    p      _3ap      41768444     36811812    9.8gb
13    p      _3sa      41426352     37752402    9.8gb
13    r      _3sa      41426352     37752402    9.8gb
6     r      _38z      40454765     38467877    9.8gb
13    r      _189q    114954855     18178509    9.8gb
12    p      _1eza     80697682     14544098    9.8gb
19    p      _3gw      43189550     28990898    9.8gb
19    r      _3gw      43189550     28990898    9.8gb
10    p      _3if      40906355     32480553    9.8gb
10    r      _3if      40906393     32480515    9.8gb
5     p      _3lb      39564296     28918504    9.8gb
2     r      _3ez      42572745     30059692    9.8gb
2     p      _3ez      42572745     30059692    9.8gb
1     p      _hql      86588975     30345199    9.8gb
3     r      _316      40351657     26276060    9.8gb
3     p      _316      40351658     26276059    9.8gb
13    p      _4ah      42486055     40258526    9.8gb
6     p      _y3y      63205330     23592500    9.7gb
17    r      _3r7      42313562     35267386    9.7gb
17    p      _3r7      42313562     35267386    9.7gb
8     p      _30g      34440167     23851639    9.7gb
8     r      _30g      34440162     23851644    9.7gb
12    r      _37l      39738962     36979585    9.7gb
12    p      _37l      39738961     36979586    9.7gb
6     r      _2w7      36563628     23179883    9.7gb
6     p      _2w7      36563628     23179883    9.7gb
16    p      _dki      53470087     48559144    9.7gb
16    p      _1bza    116655589     16518273    9.7gb
17    r      _3by      36118855     20128641    9.7gb
17    p      _3by      36118855     20128641    9.7gb
1     p      _2us      42111947     26149803    9.7gb
1     r      _2us      42111948     26149802    9.7gb
0     r      _vtw     109699503     29889414    9.7gb
10    r      _1gqi    120035598      4972206    9.7gb
15    p      _38z      37949339     32939767    9.7gb
7     p      _30a      35135691     20381116    9.7gb
7     r      _30a      35135691     20381116    9.7gb
15    r      _12je     52773082     21498169    9.6gb
3     p      _3hv      42028916     28682371    9.6gb
3     r      _3hv      42028915     28682372    9.6gb
14    r      _2w6      33721942     27582136    9.6gb
14    p      _2w6      33721942     27582136    9.6gb
14    p      _yg6      78404351     25749397    9.6gb
9     p      _3ld      39155537     36741081    9.6gb
9     r      _3ld      39155537     36741081    9.6gb
17    r      _ndx     118023723     17407314    9.6gb
7     p      _3g2      43357645     39272763    9.6gb
7     r      _3g2      43357645     39272763    9.6gb
15    p      _2x4      33554369     29732620    9.6gb
11    r      _31b      35522492     19479117    9.6gb
11    p      _31b      35522492     19479117    9.6gb
9     p      _2ya      33366087     22098530    9.6gb
9     r      _2ya      33366087     22098530    9.6gb
12    r      _2ps      35047741     26749232    9.5gb
12    p      _2ps      35047740     26749233    9.5gb
2     r      _35c      39233107     21254305    9.5gb
2     p      _35c      39233107     21254305    9.5gb
19    p      _31b      35716212     20988646    9.5gb
19    r      _31b      35716213     20988645    9.5gb
0     p      _2xt      38223320     20124901    9.5gb
0     r      _2xt      38223320     20124901    9.5gb
16    r      _dk5      55147423     45134514    9.4gb
10    p      _3a6      32763135     21189776    9.4gb
10    r      _3a6      32763153     21189758    9.4gb
15    r      _19za     50645901     13790551    9.3gb
2     r      _1731     92635075     10069092    9.3gb
12    r      _16lb     82055613     11809701    9.2gb
12    r      _wur      52467130     23215641    9.2gb
6     p      _dbv      47757289     40698673    9.2gb
12    p      _11al     60603152     20178802    9.2gb
5     p      _36j      33311098     19467977      9gb
5     r      _36j      33311068     19468007      9gb
5     r      _12ei     58564267     24891531    8.9gb
8     p      _1b9w     81460778      6790266    8.8gb
9     p      _zzc      81493950     10899083    8.6gb
0     r      _11id     54353984     24186704    8.5gb
3     p      _gsb      69420883     27744017      8gb
19    r      _o1x      78913766     21102513    7.9gb
6     r      _knj      84615375     22736621    7.7gb
16    r      _vjz      79414064     31512784    7.7gb
1     r      _fm1      48956209     20831780    7.1gb
8     r      _gw9      54321711     24086398      7gb
0     p      _s1v      70665974     21685571    6.8gb
5     r      _rmv      77063016     22930084    6.7gb
12    r      _qtw      77729117     19870623    6.7gb
15    r      _txn      73758946     18977539    6.3gb
16    r      _ifr      68438462     18131312      6gb
12    p      _s9h      63044959     17512580      6gb
6     r      _1bsa     60499032     14553018    5.5gb
3     p      _1d8w     64778219     10749228    5.4gb
11    p      _1lqa     62887230      5837089    5.2gb
3     r      _1cl7     56774182     16756769    5.1gb
1     r      _1199     53917168     22182117      5gb
15    p      _13c8     44238501     24867030    4.6gb
6     p      _1lny     48196054      6992339    4.3gb
13    p      _1bpo     42263090      9760498    4.1gb
11    r      _1400     31651223     21917068    4.1gb
7     r      _1bl0     37112484     22785724    4.1gb
17    r      _1hxb     49108226      3764225      4gb
0     p      _1jm1     38700985      9141620    3.6gb
14    p      _1gnr     35631954      9627453    3.5gb
4     r      _1qii     40496050      5208017    3.5gb
11    r      _1ng1     40886001      3731942    3.5gb
15    p      _1lhq     38497802      6495377    3.4gb
7     r      _1vha     40564774      2478961    3.4gb
9     p      _16lg     26893147     16799569    3.3gb
2     r      _1kn3     39835410      2548978    3.3gb
8     r      _1ef6     26155906     16935767    3.3gb
4     p      _1c2g     29443734     12705732    3.2gb
1     r      _1dwp     33999449      8573252    3.2gb
9     r      _1i5w     30744930      8774230    3.1gb
1     p      _1qgv     35704112      1485598    2.9gb
0     r      _1c88     23271752     14941311    2.9gb
19    r      _1fic     25179140      8659931    2.7gb
8     r      _1uhr     32174340      2062898    2.7gb
15    r      _1llb     27581351      5607336    2.6gb
8     p      _1b7p     21573443     10266084    2.6gb
18    p      _1g9y     19466063     10500958    2.4gb
17    p      _1hf6     20778967      8654081    2.4gb
18    r      _17sk     20217545      8988113    2.3gb
14    r      _1ozi     27989999      1790503    2.3gb
9     p      _1g74     22754618      6040826    2.2gb
13    r      _1bn8     17149140      7478641      2gb
10    p      _15xl     15135285      9323176      2gb
18    p      _1vf2     24308622      1307635    1.9gb
10    p      _1fzo     19641597      5525929    1.9gb
10    r      _1lgg     20366863      4896577    1.9gb
7     p      _1oww     21494857      2868470    1.8gb
19    p      _1hdf     14704452      8319770    1.7gb
5     p      _1hlf     14501886      7034068    1.7gb
13    r      _1lt5     17393376      5606856    1.7gb
16    p      _1mdt     16818583      5726255    1.7gb
6     r      _1mc1     16627885      4938357    1.7gb
3     r      _1k2j     14067000      7370178    1.6gb
8     p      _1lgq     15800787      5605119    1.6gb
0     r      _1ocn     14621978      5797224    1.6gb
4     p      _1lf9     15404158      4488559    1.6gb
3     p      _1irt     14168210      5894554    1.5gb
12    p      _1lgr     12503702      6125486    1.5gb
16    r      _1ms4     13611361      6546326    1.5gb
12    r      _1etk     13810678      5644711    1.5gb
0     p      _1qns     14572003      5227058    1.4gb
1     r      _1mnc     16729453       910652    1.3gb
17    p      _1r8n     12082132      5324042    1.2gb
16    r      _1gdk     11045452      5806432    1.2gb
12    p      _1tpm     14587792      2849409    1.2gb
9     r      _1q3o     15782278       344166    1.2gb
5     p      _1q0x     14431437      2258955    1.2gb
19    p      _1ohq     14287593      1416019    1.2gb
5     p      _1dem      8830514      4618271    1.1gb
18    r      _1hlv     11793358      3058883      1gb
2     p      _1sh6      8082350      4749890 1003.5mb
0     r      _1irb      8202789      3888273  986.7mb
14    p      _1kme      6405036      5999344  912.8mb
13    p      _1h0u     10669552      2146779  877.8mb
4     r      _1s2p      8007416      3623069  875.3mb
18    r      _1ft3      6802930      3499524  864.8mb
12    r      _1g5f      7064988      4034724  812.2mb
19    r      _1j4l      6050884      4146362  807.3mb
4     p      _1pcj      9798615       628637  804.3mb
9     p      _1joe      9197595       634500  756.3mb
16    r      _1qn9      8251125       413002    707mb
3     r      _1qqp      7527468      1831656  703.9mb
13    p      _1jpp      7357820       225984  687.5mb
17    p      _1vxj      6901703      1106979  684.9mb
11    p      _1pc7      8038347       363158  679.4mb
6     r      _1pco      7736067       585940  673.4mb
14    p      _1o8p      8337883       540710  671.9mb
3     r      _1rln      6509848       212101  603.1mb
15    p      _1pv4      6172931       333510  586.8mb
19    r      _1kcs      6349668      1970151  571.4mb
12    r      _1ir1      5941079       222076  559.5mb
16    p      _1ohc      6500643      1538946  558.6mb
17    p      _1ss1      4049146      3614691  540.8mb
0     r      _1r56      6132013      1171578  529.1mb
3     p      _1jqu      5229145      1889762  528.9mb
15    r      _1oi6      5774341       367151    503mb
15    p      _1my0      4916517      2540830  497.9mb
2     p      _1wh0      4968189        95434  472.5mb
16    p      _1qxg      4601581       571744  456.3mb
17    r      _1k73      4608602       197332  443.4mb
10    p      _1i64      4514395       992235  427.5mb
5     r      _1lni      3372791      2759117  400.8mb
18    r      _1kir      4057567        32384  386.5mb
8     p      _1oox      4353131       187538  384.8mb
6     p      _1pjl      3877841       186217  381.9mb
11    r      _1qaa      3921957        54071  373.8mb
```

  

这个大小要慢慢增大 不然会一次性merge

```Bash
PUT /ads_large_clazz_user_index_v3/_settings
{
  "index": {
    "merge": {
      "policy": {
        "max_merged_segment": "15gb"  
      }
    }
  }
}
```

  

完成后记得：

调整 max_merged_segment = 5gb 新产生的 Segment 会控制在 5GB 以内