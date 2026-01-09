

### 物化视图


1. ClickHouse 物化视图可以做什么?
    
    - 物化视图是一种预先计算并存储查询结果的技术,可以大大提高查询性能。
    - 物化视图可以用来做数据聚合、预计算、数据清洗等操作,为后续的查询提供快速的结果。
2. 为什么做聚合需要物化视图?
    
    - 对于复杂的聚合查询,直接在原始数据上进行计算会非常慢。
    - 使用物化视图可以预先计算好聚合结果,大大提高查询速度。
    - 物化视图会定期自动更新,保证数据的实时性。
3. 为什么物化视图会快?
    
    - 物化视图将查询结果预先计算并存储,避免了每次查询时重复计算。
    - ClickHouse 的列式存储和压缩技术可以大大减少磁盘 I/O,提高查询速度。
    - 物化视图可以针对特定的查询场景进行优化,比如使用合适的分区和索引。
4. 物化视图本质上是什么?
    
    - 物化视图本质上是一张预先计算好的表,存储了查询的结果数据。
    - 当查询条件命中物化视图时,ClickHouse 会直接从物化视图中读取数据,而不需要重新计算。
    - 物化视图会定期自动更新,保证数据的实时性。

总之,ClickHouse 的物化视图是一种非常强大的性能优化技术,可以大大提高复杂查询的速度,是 ClickHouse 高性能的重要保证。

##### 物化视图会定期自动更新,保证数据的实时性。 这个是怎么保证的

ClickHouse 中物化视图的自动更新是通过以下几个机制来实现的:

1. 增量更新:
    
    - ClickHouse 会监控原始数据表的变化,只对发生变化的部分进行增量更新,而不是全表重算。
    - 这样可以大大提高更新效率,保证物化视图的数据实时性。
2. 后台异步更新:
    
    - ClickHouse 会在后台自动定期检查物化视图是否需要更新,并异步进行更新操作。
    - 这样可以避免物化视图更新对用户查询造成阻塞。
3. 刷新触发机制:
    
    - 当原始数据表发生变化时,ClickHouse 会自动触发物化视图的刷新。
    - 用户也可以手动触发物化视图的刷新操作。
4. 版本控制:
    
    - ClickHouse 会为物化视图维护多个版本,保证查询时读取到最新的数据。
    - 旧版本的物化视图会在新版本生成后被逐步删除。

通过上述机制,ClickHouse 可以确保物化视图的数据实时性,同时又不会影响用户的查询性能。这是物化视图能够大幅提高查询速度的关键所在。


物化视图确实也有一些缺点和局限性,需要根据具体的应用场景来评估是否使用:

1. 维护成本:
    
    - 物化视图需要定期更新,会增加系统的维护成本和复杂度。
    - 如果原始数据表变化频繁,需要更新物化视图的成本会比较高。
2. 存储空间占用:
    
    - 物化视图会占用额外的存储空间,可能会增加整体的存储成本。
    - 对于一些数据量较大的场景,物化视图的存储开销可能会很高。
3. 不适用于实时分析:
    
    - 物化视图虽然可以提高查询性能,但更新存在一定的延迟。
    - 对于需要实时分析的场景,物化视图可能不太适用。

因此,物化视图更适用于以下场景:

1. 复杂查询场景:
    
    - 当查询涉及大量的聚合、连接等操作时,使用物化视图可以大幅提高查询性能。
2. 重复查询场景:
    
    - 如果有一些固定的报表查询,使用物化视图可以避免每次都重新计算。
3. 数据仓库场景:
    
    - 在数据仓库中,物化视图可以帮助优化复杂的 OLAP 查询。

对于一些实时性要求较高,或数据量较小的场景,可能不需要使用物化视图。需要根据具体情况进行权衡和选择。






### 使用kakfa引擎表
```

`CREATE TABLE wly_operation_log (`

`log_type Int32 COMMENT` `'日志类型: 属性变更,任务变更'``,`

`sub_log_type Int32 COMMENT` `'具体的子日志类型: 分配任务,执行完成,任务取消'``,`

`resource_id String COMMENT` `'资源id'``,`

`updated_field String COMMENT` `'更新的字段'``,`

`updated_field_desc String COMMENT` `'更新的字段的中文描述'``,`

`origin_value String COMMENT` `'更新前的值'``,`

`origin_value_desc String COMMENT` `'更新前的值的中文描述'``,`

`updated_value String COMMENT` `'更新后的值'``,`

`updated_value_desc String COMMENT` `'更新后的值的中文描述'``,`

`main_task_id String COMMENT` `'主任务id'``,`

`sub_task_id String COMMENT` `'子任务id'``,`

`status String COMMENT` `'任务状态(包含子任务, 主任务) wly_sub_task表'``,`

`status_desc String COMMENT` `'任务状态描述(包含子任务, 主任务) wly_sub_task表'``,`

`reason String COMMENT` `'失败原因'``,`

`table_name String COMMENT` `'表名: 记录变更的表名'``,`

`operator String COMMENT` `'操作人'``,`

`update_time DATETIME(``'Asia/Shanghai'``) COMMENT` `'原始表的update_time字段'``,`

`operation_time DATETIME(``'Asia/Shanghai'``) COMMENT` `'操作人操作时间, 如果是系统执行时间, 两个字段值一样'``,`

`operator_id String COMMENT` `'操作id, 最好直接用qinzhou的EagleEye-TraceID, 方便直接查日志'``,`

`created_at DATETIME(``'Asia/Shanghai'``) DEFAULT now() COMMENT` `'入库时间'`

`) ENGINE = ReplicatedMergeTree()`

`PARTITION BY toYYYYMM(operation_time)`

`ORDER BY (resource_id, operation_time, sub_log_type, updated_field)`

`TTL operation_time + toIntervalDay(``180``)`

`SETTINGS index_granularity =` `8192``;`

`CREATE TABLE wly_operation_log_kafka`

`(`

`` `log_type` Int32 COMMENT `` `'日志类型: 属性变更,任务变更'``,`

`` `sub_log_type` Int32 COMMENT `` `'具体的子日志类型: 分配任务,执行完成,任务取消'``,`

`` `resource_id` String COMMENT `` `'资源id'``,`

`` `updated_field` String COMMENT `` `'更新的字段'``,`

`` `updated_field_desc` String COMMENT `` `'更新的字段的中文描述'``,`

`` `origin_value` String COMMENT `` `'更新前的值'``,`

`` `origin_value_desc` String COMMENT `` `'更新前的值的中文描述'``,`

`` `updated_value` String COMMENT `` `'更新后的值'``,`

`` `updated_value_desc` String COMMENT `` `'更新后的值的中文描述'``,`

`` `main_task_id` String COMMENT `` `'主任务id'``,`

`` `sub_task_id` String COMMENT `` `'子任务id'``,`

`` `status` String COMMENT `` `'任务状态(包含子任务, 主任务) wly_sub_task表'``,`

`` `status_desc` String COMMENT `` `'任务状态描述(包含子任务, 主任务) wly_sub_task表'``,`

`` `reason` String COMMENT `` `'失败原因'``,`

`` `table_name` String COMMENT `` `'表名: 记录变更的表名'``,`

`` `operator` String COMMENT `` `'操作人'``,`

`` `update_time` DATETIME( ```'Asia/Shanghai'``) COMMENT` `'原始表的update_time字段'``,`

`` `operation_time` DATETIME( ```'Asia/Shanghai'``) COMMENT` `'操作人操作时间, 如果是系统执行时间, 两个字段值一样'``,`

`` `operator_id` String COMMENT `` `'操作id, 最好直接用qinzhou的EagleEye-TraceID, 方便直接查日志'``,`

`` `created_at` DATETIME( ```'Asia/Shanghai'``) COMMENT` `'入库时间'`

`)`

`ENGINE = Kafka()`

`SETTINGS kafka_broker_list =` `'172.16.24.183:9092'``,`

`kafka_topic_list =` `'gaotu_wly_operation_log_ck_prod'``,`

`kafka_group_name =` `'gaotu_wly_operation_log_ck_group'``,`

`kafka_skip_broken_messages=``1``,`

`kafka_commit_every_batch =` `1``,`

`kafka_num_consumers=``4``,`

`kafka_format =` `'JSONEachRow'``;`

`CREATE MATERIALIZED VIEW wly_operation_log_materialized_view TO wly_operation_log AS`

`SELECT log_type, sub_log_type, resource_id, updated_field, updated_field_desc, origin_value, origin_value_desc, updated_value, updated_value_desc, main_task_id, sub_task_id, status, status_desc, reason, table_name, operator, update_time, operation_time, operator_id`

`FROM wly_operation_log_kafka ;`
```

  
OLTP（Online Transaction Processing，联机事务处理）和OLAP（Online Analytical Processing，联机分析处理）是两种常见的数据库处理方式，用于不同类型的数据处理和分析需求。它们在目标、数据结构、查询模式和适用场景等方面有着明显的差异。

### OLTP（联机事务处理）：

1. **目标**：
    
    - OLTP 主要用于处理日常的业务事务，如交易记录、订单处理、客户管理等。
    - 它侧重于处理大量的短期事务，并保证数据的一致性和准确性。
2. **数据结构**：
    
    - 数据通常以规范化的方式存储，即将数据分解成多个相关的表，以减少数据冗余和提高数据更新效率。
    - 每个事务通常只涉及少量的数据行，并且要求较高的数据一致性。
3. **查询模式**：
    
    - OLTP 查询通常是简单的增删改查操作，针对具体的业务对象，如插入订单、更新客户信息等。
    - 查询通常是针对单个事务或少量事务的操作，响应时间通常较短。
4. **适用场景**：
    
    - OLTP 适用于需要处理大量并发事务、要求快速响应时间和保证数据一致性的业务应用，如电子商务、在线银行、在线预订等。

### OLAP（联机分析处理）：

1. **目标**：
    
    - OLAP 主要用于执行复杂的数据分析和查询，如多维分析、数据挖掘、报表生成等。
    - 它侧重于从大规模的数据集中提取、分析和汇总数据，以支持决策制定和业务洞察。
2. **数据结构**：
    
    - 数据通常以维度模型（如星型模型或雪花模型）的方式组织，包括事实表和维度表，以支持多维分析。
    - 数据往往以聚合的形式存储，以提高查询性能和加快分析速度。
3. **查询模式**：
    
    - OLAP 查询通常是复杂的多维分析查询，涉及到大量的数据聚合、切片、切块、钻取等操作。
    - 查询通常是针对历史数据或整个数据集的分析，响应时间可以较长。
4. **适用场景**：
    
    - OLAP 适用于需要进行大规模数据分析和洞察的场景，如数据仓库、业务智能、报表分析、市场营销分析等。

综上所述，OLTP 和 OLAP 在目标、数据结构、查询模式和适用场景等方面有着明显的差异，分别适用于处理日常业务事务和执行复杂的数据分析和查询。


### 索引

**在稠密索引中每一行索引标记都会对应到一行具体的数据记录。而在稀疏索引中，每一行索引标记对应的是一段数据，而不是一行**。

![[../../壁纸/附件/Pasted image 20240523135613.png]]

用一个形象的例子来说明：如果把MergeTree比作一本书，那么稀疏索引就好比是这本书的一级章节目录。一级章节目录不会具体对应到每个字的位置，只会记录每个章节的起始页码。

