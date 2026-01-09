
Strean流的Debug

1. ![[../../壁纸/附件/Pasted image 20240807214300.png]]
![[../../壁纸/附件/Pasted image 20240807214324.png]]

# 远程Debug


![[../../壁纸/附件/Pasted image 20250512165742.png]]
### 如何判断是否已被连接


Test环境没有办法debug

```
netstat -anp | grep 28666


```


```
tcp  0  0 10.218.238.170:28666 10.10.1.12:57432 ESTABLISHED 12345/java

```

表示：已经有一台 IP 为 `10.10.1.12` 的机器连上了。


![[../../壁纸/附件/Pasted image 20250512165705.png]]