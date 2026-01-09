
字段 

![[../../../壁纸/附件/Pasted image 20250826140146.png]]

http://genshuixue-public.oss-cn-beijing.aliyuncs.com/origin_test/2026-01-09/acd545df28f813bab103a4ee798fddd2/iShot_2025-08-26_13.52.12.mp4



![[../../../壁纸/附件/iShot_2025-08-26_16.06.45.mp4]]

页面报错 是因为 字段重复导致



```
select * from ees_data.student_field_config where field_name = 'studentConstellationTest'


```



cds找不到字段 是因为数据种类没配

数据种类是数据类型的细化类型  是用来额外补偿数据类型的  cds需要更细化类型  需要设置种类 

设置完之后有缓存 需要等待几分钟
![[../../../壁纸/附件/Pasted image 20250903144427.png]]


未建字段