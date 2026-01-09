

student-center

com.gaotu.yunying.student.center.job.mq.consumer.ons.DwsFuwuCallRecordListener


```
__tag__:environment: prod* not __tag__:_container_name_: mesh and messages:"student-center-dynamic-history-prod" and messages: OnsMqProducer and messages: subDynamicType and messages: 5 and messages: "131587"


```

student-data-dws

com.gaotu.student.data.dws.mq.dws.call.DwsFuwuCallRecordConsumer


bdg_dwd_call_record_all_rt

根据userId查询
```
__tag__:app: "student-data-dws" AND __tag__:environment: prod* not __tag__:_container_name_: mesh and messages: "fuwu_call_record_event_prod" and messages: "4868789944"
```