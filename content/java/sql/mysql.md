
### 事务 批量更新 导致死锁的问题 事务死锁

```

org.springframework.dao.DeadlockLoserDataAccessException: 
### Error updating database.  Cause: com.mysql.cj.jdbc.exceptions.MySQLTransactionRollbackException: Deadlock found when trying to get lock; try restarting transaction
```

 SQL 的锁定顺序不一致

例如：

- 线程 A 更新 `id=101`，再更新 `id=102`
    
- 线程 B 更新 `id=102`，再更新 `id=101`
    

→ 这就是典型的 **死锁锁等待交叉**，MySQL 无法自动处理，只能中断其中一个事务。



![[../../壁纸/附件/Pasted image 20250514181627.png]]

![[../../壁纸/附件/Pasted image 20250514181620.png]]






1. 反斜杠自动转义的问题
	> select @@sql_mode;
SET sql_mode='NO_BACKSLASH_ESCAPES';
SET sql_mode='';



2. 首字母大写 转为小写
``` mysql
UPDATE tb_sales_cas_wxid_u_record  
SET cas_id = LOWER(cas_id)  
WHERE BINARY LEFT(cas_id,1) BETWEEN 'A' AND 'Z' limit 1000;  
  
SELECT id, cas_id  
FROM tb_sales_cas_wxid_u_record  
WHERE BINARY LEFT(cas_id, 1) BETWEEN 'A' AND 'Z';
```



3. 该错误为 MySQL 解析 SQL 时语法异常，出现在列列表中使用了保留关键字 `order` 和 `desc`，未加反引号或改名，导致解析失败。

该错误为 MySQL 解析 SQL 时语法异常，出现在列列表中使用了保留关键字 `order` 和 `desc`，未加反引号或改名，导致解析失败。


![[../../壁纸/附件/Pasted image 20250424143208.png]]