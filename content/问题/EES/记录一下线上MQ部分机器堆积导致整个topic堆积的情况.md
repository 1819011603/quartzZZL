

1. 如何查看每个机器的堆积情况

	消息队列 RocketMQ  -> /实例列表 -> Group 管理 -> Group 详情 -> 基本信息
![[../../壁纸/附件/Pasted image 20250123092838.png]]
查看堆积的机器 监听了 多少个partition
```shell
watch com.gaotu.student.data.dws.mq.statistic.caculate.DwsLessonLiveExamConsumer consume '@com.alibaba.fastjson.JSON@toJSONString(params[0].getTopicPartition() )' -n 50 -x 3
```

2. 获取topic的partition数量  (使用MessageListener方式)


调用该命令获取

```shell
sc -d com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.factory.MQClientInstance
```

```shell
vmtool -x 3 --action getInstances --className com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.factory.MQClientInstance  --express '@com.alibaba.fastjson.JSONObject@toJSONString(instances.{topicRouteTable})'  -c 7674a051

vmtool -x 3 --action getInstances --className com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.factory.MQClientInstance  --express '@com.alibaba.fastjson.JSONObject@toJSONString(instances.{producerTable})'  -c 7674a051
```




1. 获取topic的partition数量  (使用MessageListener方式) 直接搜topic名称就知道partition数量了


调用该命令获取

```shell
			sc -d com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.factory.MQClientInstance
```

```shell
vmtool -x 3 --action getInstances --className com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.factory.MQClientInstance  --express '@com.alibaba.fastjson.JSONObject@toJSONString(instances.{topicRouteTable})'  -c 69c43e48
```


使用策略模式

```
sc -d org.apache.rocketmq.client.impl.factory.MQClientInstance
```

```
vmtool -x 3 --action getInstances --className org.apache.rocketmq.client.impl.factory.MQClientInstance  --express '@com.alibaba.fastjson.JSONObject@toJSONString(instances.{topicRouteTable})'  -c 1b39fd82
```



partition的定义就是一个队列

```java
String partition = messageQueue.getBrokerName() + '#' + messageQueue.getQueueId();
```
![[../../壁纸/附件/Pasted image 20250123112719.png]]


搜索topic获取查看queueDatas读写实例数量和读写队列数量

![[../../壁纸/附件/Pasted image 20250123112946.png]]

![[../../壁纸/附件/Pasted image 20250123113006.png]]

以这个为例,
实例名称为  vip-cn-beijing-uqm3hjaby01-0, vip-cn-beijing-uqm3hjaby01-1, vip-cn-beijing-uqm3hjaby01-2

读队列数和写队列数都是8

partition的数量为 8+ 8+ 8 = 24





3. 查看哪些数据耗时 使用watch去看

如果一直没有进去,  考虑线程池一直在跑任务, 停不下来


找for循环里面跟关键参数有关系的方法   进行watch  找到关键参数来排查问题




4. RocketMQ手动验证会使用公共线程池 不会使用原来Consumer的线程池进行消费验证

名称为  NettyClientPublicExecutor_5



最后问题是

班级下的辅导班下  有零元课赠送的辅导班 无辅导老师的空班 人数是居多的