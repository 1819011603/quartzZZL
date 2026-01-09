  



  

## 一、核心概念

  

### 1.1 为什么会有"已删除文档"？

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│                 Lucene Segment 不可变原则                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Lucene 的设计哲学：Segment 一旦写入，永不修改                   │
│                                                                 │
│  删除文档时：                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Segment_1.del 文件                                     │   │
│  │  ├── Doc 100: ✓ (存活)                                  │   │
│  │  ├── Doc 101: ✗ (已删除) ← 只是标记，数据还在            │   │
│  │  ├── Doc 102: ✓ (存活)                                  │   │
│  │  └── Doc 103: ✗ (已删除) ← 只是标记，数据还在            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ⚠️ 被标记删除的文档仍然：                                      │
│     - 占用磁盘空间                                              │
│     - 占用 Doc ID 配额                                          │
│     - 影响查询性能（需要过滤）                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

### 1.2 什么是 Merge（合并）？

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│                    Merge 合并过程                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  合并前：                                                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Segment_1    │ │ Segment_2    │ │ Segment_3    │            │
│  │ Doc 1 ✓     │ │ Doc 4 ✓     │ │ Doc 7 ✗     │            │
│  │ Doc 2 ✗     │ │ Doc 5 ✗     │ │ Doc 8 ✓     │            │
│  │ Doc 3 ✓     │ │ Doc 6 ✓     │ │ Doc 9 ✓     │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│       3 docs          3 docs          3 docs                   │
│    (1 deleted)     (1 deleted)     (1 deleted)                 │
│                                                                 │
│                         ⬇️ Merge                                │
│                                                                 │
│  合并后：                                                        │
│  ┌────────────────────────────────────────────┐                │
│  │ Segment_New                                │                │
│  │ Doc 1 ✓  (原 Seg1.Doc1)                   │                │
│  │ Doc 2 ✓  (原 Seg1.Doc3)                   │                │
│  │ Doc 3 ✓  (原 Seg2.Doc4)                   │                │
│  │ Doc 4 ✓  (原 Seg2.Doc6)                   │                │
│  │ Doc 5 ✓  (原 Seg3.Doc8)                   │                │
│  │ Doc 6 ✓  (原 Seg3.Doc9)                   │                │
│  └────────────────────────────────────────────┘                │
│       6 docs (0 deleted) ✅                                     │
│                                                                 │
│  ✅ 已删除的 Doc 2, 5, 7 被真正物理删除                         │
│  ✅ 磁盘空间被回收                                              │
│  ✅ Doc ID 配额被释放                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  



  

  

## 一、索引 Merge 配置解读

### 1.1 当前配置

JSON

```Plain
{
  "ads_large_clazz_user_index_v2": {
    "settings": {
      "index": {
        "refresh_interval": "2s",
        "number_of_shards": "5",
        "number_of_replicas": "1",
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
      }
    }
  }
}
```

### 1.2 配置问题分析

```Shell
┌─────────────────────────────────────────────────────────────────┐
│                 当前 Merge 配置的问题                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚠️ 问题 1：Merge 线程数过少                                    │
│  ────────────────────────────────────────────────────────────   │
│  配置：max_thread_count = 1, max_merge_count = 1               │
│  后果：                                                         │
│  - 同一时间只能执行 1 个 Merge 任务                             │
│  - 高频更新时，Merge 速度远跟不上 Deleted 产生速度               │
│  - Deleted 文档堆积，无法及时回收                                │
│                                                                 │
│  ⚠️ 问题 2：大 Segment 无法自动合并                             │
│  ────────────────────────────────────────────────────────────   │
│  配置：max_merged_segment = 10gb                                │
│  现状：单分片约 180GB，可能存在多个 > 10GB 的 Segment        │
│  后果：                                                         │
│  - 这些大 Segment 中的 Deleted 永远不会被自动清理               │
│  - 只能手动 Force Merge                                         │
│                                                                 │
│  ⚠️ 问题 3：floor_segment 设置偏大                              │
│  ────────────────────────────────────────────────────────────   │
│  配置：floor_segment = 50mb                                     │
│  说明：小于 50MB 的 Segment 会被视为同一层级，优先合并           │
│  问题：refresh_interval = 2s，产生的新 Segment 可能 < 50MB      │
│        导致大量小Segment 堆积后才触发合并                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

  

## 二、Merge 触发机制

  

### 2.1 触发方式概览

  

|   |   |   |   |
|---|---|---|---|
|触发方式|时机|是否阻塞写入|适用场景|
|**自动 Merge**|后台持续运行|❌ 否|日常运维|
|**手动 Force Merge**|主动调用 API|⚠️ 可能|低峰期维护|
|**Refresh 后**|新 Segment 生成时评估|❌ 否|自动触发|
|**Flush 后**|Translog 持久化后|❌ 否|自动触发|

  

### 2.2 自动 Merge 机制

  

#### 2.2.1 Merge 策略：TieredMergePolicy（默认）

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│              TieredMergePolicy 分层合并策略                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  核心思想：将 Segment 按大小分层，优先合并小的 Segment           │
│                                                                 │
│  Layer 1 (小):     [1MB] [2MB] [1MB] [3MB] → 优先合并           │
│  Layer 2 (中):     [50MB] [60MB] [40MB]    → 次优先             │
│  Layer 3 (大):     [500MB] [600MB]         → 较少合并           │
│  Layer 4 (超大):   [2GB] [3GB]             → 很少合并           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

#### 2.2.2 关键参数

  

```JSON
PUT /my_index/_settings
{
  "index": {
    "merge": {
      "policy": {
        // 单个 Segment 最大大小，超过此值不再参与普通合并
        "max_merged_segment": "5gb",
        
        // 每层最多允许的 Segment 数量
        "segments_per_tier": 10,
        
        // 一次合并最多包含的 Segment 数量
        "max_merge_at_once": 10,
        
        // 触发合并的最小 Segment 数量
        "min_merge_at_once": 2,
        
        // 已删除文档占比超过此值时，强制参与合并
        "expunge_deletes_allowed": 10,
        
        // floor_segment: 小于此值的 Segment 被视为同一层级
        "floor_segment": "2mb"
      },
      "scheduler": {
        // 最大并发 Merge 线程数
        "max_thread_count": 1,
        
        // 最大并发 Merge 任务数
        "max_merge_count": 6
      }
    }
  }
}
```

  

#### 2.2.3 自动 Merge 触发条件

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│                自动 Merge 触发条件判断                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  条件 1：Segment 数量超过阈值                                    │
│  ────────────────────────────────────────────────────────────   │
│  当同一层级的 Segment 数量 > segments_per_tier (默认 10)        │
│  → 触发合并，将多个小 Segment 合并为一个大 Segment              │
│                                                                 │
│  条件 2：已删除文档占比过高                                      │
│  ────────────────────────────────────────────────────────────   │
│  当 Segment 中 deleted_docs / total_docs > 阈值 (默认 10%)      │
│  → 该 Segment 被标记为"需要合并"                                │
│                                                                 │
│  条件 3：新 Segment 产生后的评估                                 │
│  ────────────────────────────────────────────────────────────   │
│  每次 Refresh 产生新 Segment 后，都会评估是否需要合并            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

### 2.3 自动 Merge 的执行流程

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│                 自动 Merge 完整流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐                                                │
│  │   写入请求   │                                                │
│  └──────┬──────┘                                                │
│         ▼                                                       │
│  ┌─────────────┐                                                │
│  │ Memory Buffer│ ← 写入内存                                    │
│  └──────┬──────┘                                                │
│         ▼ (每秒 Refresh)                                        │
│  ┌─────────────┐                                                │
│  │ New Segment │ ← 生成新的小 Segment                           │
│  └──────┬──────┘                                                │
│         ▼                                                       │
│  ┌─────────────────────────────────────┐                        │
│  │ Merge Policy 评估                   │                        │
│  │ ├── 检查 Segment 数量               │                        │
│  │ ├── 检查 deleted 比例               │                        │
│  │ └── 决定是否触发 Merge              │                        │
│  └──────┬──────────────────────────────┘                        │
│         │                                                       │
│    ┌────┴────┐                                                  │
│    ▼         ▼                                                  │
│  [不合并]  [触发合并]                                            │
│              │                                                  │
│              ▼                                                  │
│  ┌─────────────────────────────────────┐                        │
│  │ Merge Scheduler 调度                │                        │
│  │ ├── 加入 Merge 队列                 │                        │
│  │ ├── 等待 Merge 线程                 │                        │
│  │ └── 后台异步执行                    │                        │
│  └──────┬──────────────────────────────┘                        │
│         ▼                                                       │
│  ┌─────────────────────────────────────┐                        │
│  │ 执行 Merge                          │                        │
│  │ ├── 读取多个旧 Segment              │                        │
│  │ ├── 跳过 deleted 文档               │  ← ⭐ 真正删除发生在这里│
│  │ ├── 写入新 Segment                  │                        │
│  │ ├── 更新 Segment 元信息             │                        │
│  │ └── 删除旧 Segment 文件             │                        │
│  └─────────────────────────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

---

  

## 三、手动 Force Merge

  

### 3.1 Force Merge API

  

```Bash
# 基础用法：合并到 N 个 Segment
POST /my_index/_forcemerge?max_num_segments=1

# 只清理已删除文档，不强制减少 Segment 数量
POST /my_index/_forcemerge?only_expunge_deletes=true

# 完整参数
POST /my_index/_forcemerge
  ?max_num_segments=1           # 目标 Segment 数量
  &only_expunge_deletes=false   # 是否只清理删除
  &flush=true                   # 合并后是否 Flush
  &wait_for_completion=true     # 是否等待完成
```

  

### 3.2 Force Merge 适用场景

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│                Force Merge 适用场景                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 推荐使用：                                                   │
│  ├── 只读索引（历史数据、日志归档）                              │
│  ├── 大量删除后的清理                                           │
│  ├── 低峰期的定期维护                                           │
│  └── Reindex 完成后的优化                                       │
│                                                                 │
│  ❌ 不推荐使用：                                                 │
│  ├── 活跃写入的索引（会造成资源竞争）                            │
│  ├── 业务高峰期（IO 密集，影响性能）                             │
│  └── 频繁执行（浪费资源，自动 Merge 足够）                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

### 3.3 Force Merge 的风险

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│                Force Merge 风险提示                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚠️ 风险 1：资源消耗大                                          │
│  ────────────────────────────────────────────────────────────   │
│  - 需要读取所有参与合并的 Segment                               │
│  - 需要写入新的大 Segment                                       │
│  - 临时需要 2x 磁盘空间                                         │
│  - CPU 和 IO 密集                                               │
│                                                                 │
│  ⚠️ 风险 2：可能阻塞写入                                        │
│  ────────────────────────────────────────────────────────────   │
│  - 当 Merge 线程被占满时，新的写入可能被阻塞                    │
│  - 可能触发 es_rejected_execution_exception                    │
│                                                                 │
│  ⚠️ 风险 3：大 Segment 不再参与自动合并                         │
│  ────────────────────────────────────────────────────────────   │
│  - 合并后的超大 Segment 超过 max_merged_segment (5GB)           │
│  - 后续该 Segment 中的删除无法被自动清理                        │
│  - 只能再次手动 Force Merge                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

---

  

## 四、Deleted 文档的回收时机

  

### 4.1 完整的回收条件

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│           Deleted 文档真正被回收的条件                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  必须同时满足以下条件：                                          │
│                                                                 │
│  条件 1：所在 Segment 参与了 Merge                               │
│  ────────────────────────────────────────────────────────────   │
│  - 自动 Merge 选中了该 Segment                                  │
│  - 或者手动触发了 Force Merge                                   │
│                                                                 │
│  条件 2：Merge 过程完成                                          │
│  ────────────────────────────────────────────────────────────   │
│  - 新 Segment 写入完成                                          │
│  - 旧 Segment 标记为待删除                                      │
│                                                                 │
│  条件 3：旧 Segment 无引用                                       │
│  ────────────────────────────────────────────────────────────   │
│  - 没有正在进行的搜索引用该 Segment                             │
│  - 没有正在进行的 Snapshot 引用                                 │
│                                                                 │
│  条件 4：物理删除旧 Segment                                      │
│  ────────────────────────────────────────────────────────────   │
│  - 删除旧的 .si, .doc, .pos 等文件                              │
│  - 此时磁盘空间才真正释放                                       │
│  - Doc ID 配额才真正回收                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

### 4.2 为什么大 Segment 中的删除不会被回收？

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│              大 Segment 不参与自动 Merge                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  默认配置: max_merged_segment = 5GB                             │
│                                                                 │
│  场景：                                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Segment_Big (6GB)                                       │   │
│  │ ├── Live Docs:    500 万                                │   │
│  │ └── Deleted Docs: 200 万 (28.5%)  ← 大量删除！          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  问题：                                                          │
│  - 该 Segment 大小 > max_merged_segment (5GB)                   │
│  - 自动 Merge 策略会跳过它                                      │
│  - 即使 deleted 比例很高，也不会被清理                          │
│                                                                 │
│  解决：                                                          │
│  - 手动执行 Force Merge                                         │
│  - 或调大 max_merged_segment 参数                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

---

  

## 五、监控 Merge 状态

  

### 5.1 查看 Segment 信息

  

```Bash
# 查看索引的 Segment 概况
GET /my_index/_segments

# 返回示例
{
  "indices": {
    "my_index": {
      "shards": {
        "0": [{
          "segments": {
            "_0": {
              "generation": 0,
              "num_docs": 10000,        // 存活文档数
              "deleted_docs": 2000,     // 已删除文档数
              "size_in_bytes": 52428800,
              "committed": true,
              "search": true,
              "version": "8.x",
              "compound": true
            },
            "_1": {
              "generation": 1,
              "num_docs": 8000,
              "deleted_docs": 500,
              "size_in_bytes": 41943040
              // ...
            }
          }
        }]
      }
    }
  }
}
```

  

### 5.2 查看 Merge 统计

  

```Bash
# 查看 Merge 统计信息
GET /my_index/_stats/merge

# 返回示例
{
  "indices": {
    "my_index": {
      "primaries": {
        "merges": {
          "current": 0,                    // 当前正在进行的 Merge 数
          "current_docs": 0,               // 当前正在合并的文档数
          "current_size_in_bytes": 0,      // 当前正在合并的大小
          "total": 156,                    // 历史总 Merge 次数
          "total_time_in_millis": 328493,  // 历史总 Merge 耗时
          "total_docs": 28394023,          // 历史总合并文档数
          "total_size_in_bytes": 12884901888,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 45023  // 被限流的时间
        }
      }
    }
  }
}
```

  

### 5.3 查看 Deleted 比例

  

```Bash
# 查看文档统计（含 deleted）
GET /my_index/_stats/docs

# 返回示例
{
  "indices": {
    "my_index": {
      "primaries": {
        "docs": {
          "count": 15670314,    // 存活文档
          "deleted": 5804520    // 已删除文档（待回收）
        }
      }
    }
  }
}
```

  

### 5.4 监控脚本示例

  

```Bash
#!/bin/bash
# 监控 deleted 文档比例

INDEX="ads_large_clazz_user_index_v3"

result=$(curl -s "http://localhost:9200/${INDEX}/_stats/docs")

count=$(echo $result | jq '.indices["'$INDEX'"].primaries.docs.count')
deleted=$(echo $result | jq '.indices["'$INDEX'"].primaries.docs.deleted')

ratio=$(echo "scale=2; $deleted * 100 / ($count + $deleted)" | bc)

echo "Index: $INDEX"
echo "Live Docs: $count"
echo "Deleted Docs: $deleted"
echo "Deleted Ratio: ${ratio}%"

# 告警判断
if (( $(echo "$ratio > 30" | bc -l) )); then
  echo "⚠️ WARNING: Deleted ratio exceeds 30%!"
  # 发送告警...
fi
```

  

---

  

## 六、优化 Merge 策略

  

### 6.1 针对高更新场景的优化

  

```JSON
PUT /my_index/_settings
{
  "index": {
    "merge": {
      "policy": {
        // 降低触发阈值，更积极地合并
        "expunge_deletes_allowed": 5,      // 默认 10，改为 5
        "segments_per_tier": 5,            // 默认 10，改为 5
        
        // 增大单个 Segment 上限，减少 Segment 数量
        "max_merged_segment": "10gb",      // 默认 5gb
        
        // 每次合并更多 Segment
        "max_merge_at_once": 15            // 默认 10
      },
      "scheduler": {
        // 增加并发 Merge 线程（多核机器）
        "max_thread_count": 2,             // 默认 1
        "max_merge_count": 10              // 默认 6
      }
    },
    
    // 调整 Refresh 间隔，减少小 Segment 产生
    "refresh_interval": "30s"              // 默认 1s
  }
}
```

  

### 6.2 针对批量写入后的优化

  

```Bash
# 批量写入完成后，执行一次优化
# 1. 先刷新，确保数据可搜索
POST /my_index/_refresh

# 2. 等待集群空闲，执行 Force Merge
POST /my_index/_forcemerge?max_num_segments=1&wait_for_completion=false

# 3. 查看 Force Merge 进度
GET /_tasks?detailed=true&actions=*forcemerge
```

  

### 6.3 定时维护脚本

  

```Bash
#!/bin/bash
# 每周日凌晨 3 点执行

INDICES=("ads_large_clazz_user_index_v3" "other_index")
ES_HOST="http://localhost:9200"

for index in "${INDICES[@]}"; do
  echo "Processing $index..."
  
  # 1. 检查 deleted 比例
  stats=$(curl -s "${ES_HOST}/${index}/_stats/docs")
  count=$(echo $stats | jq '.indices["'$index'"].primaries.docs.count')
  deleted=$(echo $stats | jq '.indices["'$index'"].primaries.docs.deleted')
  
  if [ "$deleted" -gt 0 ]; then
    ratio=$(echo "scale=2; $deleted * 100 / ($count + $deleted)" | bc)
    echo "  Deleted ratio: ${ratio}%"
    
    # 2. 如果超过 20%，执行 Force Merge
    if (( $(echo "$ratio > 20" | bc -l) )); then
      echo "  Triggering Force Merge..."
      curl -X POST "${ES_HOST}/${index}/_forcemerge?only_expunge_deletes=true"
      echo ""
    fi
  fi
  
  sleep 5
done

echo "Maintenance completed."
```

  

---

  

## 七、Merge 过程中的问题排查

  

### 7.1 常见问题

  

|   |   |   |
|---|---|---|
|问题|可能原因|解决方案|
|Merge 速度慢|IO 瓶颈、Segment 过大|增加 Merge 线程、优化磁盘|
|Merge 被限流|store.throttle 限制|调整限流参数|
|Deleted 不减少|大 Segment 不参与合并|手动 Force Merge|
|磁盘空间不足|Merge 需要临时空间|预留 2x 空间|
|写入被阻塞|Merge 队列满|增加 max_merge_count|

  

### 7.2 查看 Merge 任务

  

```Bash
# 查看当前运行的 Merge 任务
GET /_tasks?detailed=true&actions=*merge*

# 查看节点的线程池状态
GET /_nodes/stats/thread_pool/merge

# 返回示例
{
  "nodes": {
    "node1": {
      "thread_pool": {
        "merge": {
          "threads": 2,
          "queue": 3,        // 等待中的 Merge 任务
          "active": 2,       // 正在执行的 Merge
          "rejected": 0,     // 被拒绝的（队列满）
          "largest": 2,
          "completed": 1567
        }
      }
    }
  }
}
```

  

### 7.3 Merge 限流检查

  

```Bash
# 查看 store 限流统计
GET /my_index/_stats/store

# 如果 throttle_time 很大，说明 Merge 被限流了
{
  "indices": {
    "my_index": {
      "primaries": {
        "store": {
          "size_in_bytes": 107374182400,
          "throttle_time_in_millis": 45023  // ⚠️ 被限流的时间
        }
      }
    }
  }
}

# 调整限流（提高阈值或禁用）
PUT /my_index/_settings
{
  "index.store.throttle.type": "none"  // 禁用限流（生产慎用）
}
```

  

---

  

## 八、总结

  

### 8.1 关键时间点

  

```Plain
┌─────────────────────────────────────────────────────────────────┐
│                 Deleted 文档生命周期                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  T0: Delete/Update 操作                                         │
│      └── 文档被标记为 .del，仍占用空间和 ID                     │
│                                                                 │
│  T1: 等待 Merge 选中 (不确定时间)                               │
│      └── 取决于 Segment 大小、deleted 比例、Merge 策略          │
│      └── 可能是几分钟，也可能是几天                             │
│                                                                 │
│  T2: Merge 执行中                                               │
│      └── 读取旧 Segment，跳过 deleted，写入新 Segment           │
│      └── 耗时取决于 Segment 大小，可能几秒到几小时              │
│                                                                 │
│  T3: Merge 完成                                                 │
│      └── 新 Segment 激活，旧 Segment 标记待删除                 │
│                                                                 │
│  T4: 旧 Segment 物理删除                                        │
│      └── 无引用后，删除磁盘文件                                 │
│      └── ✅ 此时 ID 配额真正回收                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

  

### 8.2 核心结论

  

|   |   |
|---|---|
|问题|答案|
|**何时回收 ID？**|Merge 完成并删除旧 Segment 后|
|**自动 Merge 会回收吗？**|会，但不保证及时（大 Segment 可能不参与）|
|**如何加速回收？**|手动 Force Merge 或调整 Merge 策略|
|**能完全回收吗？**|理论上可以，但需要所有 Segment 都参与 Merge|

  

### 8.3 最佳实践

  

|   |   |
|---|---|
|场景|建议|
|日常运维|监控 `docs.deleted` 比例，超过 20% 告警|
|大量删除后|低峰期执行 `_forcemerge?only_expunge_deletes=true`|
|只读索引|执行 `_forcemerge?max_num_segments=1` 彻底优化|
|高更新场景|调整 Merge 策略参数，增加 Merge 线程|