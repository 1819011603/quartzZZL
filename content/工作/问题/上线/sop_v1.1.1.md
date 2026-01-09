
1. 表
```sql
CREATE TABLE `tb_sales_friend_reply_conf_chatroom` (
`id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键id',
`conf_id` int(11) NOT NULL COMMENT '加好友方案id',
`chatroom_id` varchar(64) NOT NULL COMMENT '群id',
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
PRIMARY KEY (`id`),
KEY `idx_conf_id` (`conf_id`),
KEY `idx_chatroom_id` (`chatroom_id`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='加好友方案配置的接流群';
```

2. 保存原始update_sql, 用来回滚, 也可以直接使用备份回滚
3. 等待上线
4. 复制原始数据生成新的更新sql工单
	``` python
	import json,re
	
	from basicBase import fileBase, formatJson
	
	res = fileBase.getFileContentList("./chatroom.txt")
	# print("select @@sql_mode;")
	# 防止转义 防止线上事件
	# print("SET sql_mode='NO_BACKSLASH_ESCAPES';")
	pattern = "(R:\d+)"
	sql = "INSERT INTO um_individual.tb_sales_friend_reply_conf_chatroom (conf_id,chatroom_id) VALUES"
	for line in res:
	    id_pattern = r"^(\d+)"
	    json_pattern = r"(\[.*?)$"
	    id  =  re.findall(id_pattern,line)[0]
	    js = fileBase.jsonLoads(re.findall(json_pattern,line)[0])
	    p = []
	    for item in js:
	        type = item["type"]
	        if type == 6:
	            content=item["content"]
	            chatroom =  set([])
	            if content.get("wxidChatroomList") == None:
	                continue
	            for c in content["wxidChatroomList"]:
	                for ch in c["chatroom"]:
	                    chatroom.add(ch)
	            # del content["wxidChatroomList"]
	            content["chatroom"] = list(chatroom)
	            for chatroomId in chatroom:
	                sql += f'({int(id)},\'{chatroomId}\'),'
	
	            p.append(item)
	        else:
	            p.append(item)
	    p = formatJson(p)
	    p = p.replace("\n","")
	    p = p.replace(" ","")
	    p = p.replace("\\","\\\\")
	    res = 'update um_individual.tb_sales_friend_reply_by_channel_conf set conf_json=$$%s$$ where id = %s;' % (p, id)
	    print(res.replace("'",'"').replace("$$","'"))
	# print('SET sql_mode=\'\';')
	sql = sql[:-1]
	sql+=";"
	print(sql)
	```
	