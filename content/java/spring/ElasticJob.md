ElasticJob

里面的定时任务在不同的节点不应该同时进行
  
ElasticJob是一个开源的分布式作业调度解决方案，主要用于解决分布式环境下的作业调度和任务处理问题。其主要功能和用途包括：

1. **分布式作业调度**：ElasticJob可以在分布式环境下进行作业调度，支持将作业分片执行，实现任务的高可用和负载均衡。
    
2. **弹性伸缩**：ElasticJob可以根据作业的负载情况进行弹性伸缩，动态调整作业的分片数和执行节点，以提高作业执行的效率和稳定性。
    
3. **任务监控与管理**：ElasticJob提供了丰富的任务监控和管理功能，包括作业执行状态监控、任务执行日志查看、作业停止和恢复等，方便开发者对作业进行管理和调优。
    
4. **作业分片策略**：ElasticJob支持多种作业分片策略，包括固定分片数、自定义分片策略等，可以根据实际需求灵活配置作业的分片规则。
    
5. **作业调度策略**：ElasticJob支持多种作业调度策略，包括简单调度、周期调度和Cron表达式调度等，可以根据作业的执行频率和时间规律进行灵活配置。
    
6. **与Spring集成**：ElasticJob提供了与Spring框架的无缝集成，可以通过Spring的依赖注入和AOP等特性来管理和配置作业，提高开发效率和代码可维护性。
    

总的来说，ElasticJob可以帮助开发者在分布式环境下轻松实现作业调度和任务处理，提高作业执行的效率和可靠性，是分布式系统开发中常用的作业调度解决方案。



> ElasticJobConfig shardingTotalCount有什么用

在ElasticJob中，`shardingTotalCount`参数用于指定作业的分片总数。分片是将作业分成多个独立的子任务，每个子任务称为一个分片，由分片来并发执行作业，提高作业的执行效率和性能。

`shardingTotalCount`参数的作用是告诉ElasticJob当前作业需要被划分成多少个分片。根据分片总数，ElasticJob会按照一定的策略将作业的数据分配到不同的分片中，然后并发执行这些


> ElasticJob是如何将任务进行分片 然后给其他服务执行的

ElasticJob将任务进行分片并分配给其他服务执行的过程主要包括以下几个步骤：

1. **分片总数确定**：在配置ElasticJob时，需要指定作业的分片总数。这个分片总数决定了作业将被划分成多少个子任务，每个子任务即为一个分片。
    
2. **分片分配**：根据分片总数和作业名称等信息，ElasticJob使用一定的分片分配策略，例如哈希算法，将作业的数据划分到不同的分片中。每个分片包含了一部分作业的数据。
    
3. **分片执行**：ElasticJob中的分片由多个作业实例共同执行。多个作业实例会同时启动并监听同一个作业，每个作业实例根据自己被分配到的分片号，只处理属于自己负责的那部分分片数据。
    
4. **分片执行协调**：作业实例之间通过分布式协调的方式来协作执行作业。例如，它们可以利用ZooKeeper等分布式协调工具来竞选作业的领导者（Leader），由领导者负责协调分片的分配和作业的执行。
    
5. **分片执行失败处理**：如果某个作业实例由于故障或其他原因无法正常执行作业，ElasticJob会自动将该分片的执行任务重新分配给其他正常工作的作业实例，确保作业的高可用性和容错性。
    

总的来说，ElasticJob通过分片的方式将作业划分成多个子任务，并将这些子任务分配给多个作业实例共同执行，以提高作业的执行效率和容错能力。


> ElasticJob 快速上手

https://www.cnblogs.com/cjsblog/p/14295150.html

**分片项**

ElasticJob 并不直接提供数据处理的功能，而是将分片项分配至各个运行中的作业服务器，开发者需要自行处理分片项与业务的对应关系。 分片项为数字，始于 0 而终于分片总数减 1。

**个性化分片参数**

个性化参数可以和分片项匹配对应关系，用于将分片项的数字转换为更加可读的业务代码。 

合理使用个性化参数可以让代码更可读。例如，如果配置为 0=北京,1=上海,2=广州，那么代码中直接使用北京，上海，广州的枚举值即可完成分片项和业务逻辑的对应关系。


> 	shardingContext.getShardingTotalCount(),   任务总片数
	shardingContext.getShardingItem() 当前服务是第几个  

shardingContext.getShardingItem()确定当前服务处理那几个


```sql
<select id="selectByIdGreaterThan" resultMap="BaseResultMap">  
    select  
    id,url  
    from urobot.ss_wp_call_record  
    where id <![CDATA[>]]> #{maxId,jdbcType=INTEGER}  
    and MOD(id, #{shardingTotalCount}) = #{shardingItem}  
    and ext = ''  
    limit #{limitCount};  
</select>
```

 MOD(id, #{shardingTotalCount}) = #{shardingItem}  
  
这段代码是一个模板字符串，其中包含了两个变量：

- `#{shardingTotalCount}`：表示分片总数，用来对作业进行分片。
- `#{shardingItem}`：表示分片项，即作业的某个具体分片编号。

整个表达式的作用是计算一个作业的分片项。`MOD(id, #{shardingTotalCount})`表示使用id除以分片总数后取余数，得到的余数即为该作业的分片项。 得到id取余为当前服务的分片项就交给当前服务处理


**使用hset保存当前分片项处理的最大id。**
> redisClient.hset(RedisConstant.toRedisKey(DECRYPT_MP3_INDEX_KEY),  
        Integer.toString(shardingContext.getShardingItem()),  
        Integer.toString(currentProcessMaxId)


