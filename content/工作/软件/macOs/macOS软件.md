


### 代理软件:  Fiddler Everywhere 

替换软件: Reqable  下载地址: https://github.com/reqable/reqable-app/releases

http://genshuixue-public.oss-cn-beijing.aliyuncs.com/origin_test/2025-01-08/6c4c4a1becc9ae524a00d28debfa16e9/reqable-app-macos-arm64.dmg



开启重写


![[../../壁纸/附件/Pasted image 20250108181653.png]]


windows: 免费版本 Fiddler
macos 只能使用 付费版本  Fiddler Everywhere 






### MemoryAnalyzer打不开

使用java17版本的

```

The problem is that Eclipse Memory Analyser does not have enough heap space to open the Heap dump file.

You can solve the problem as follows:

1. open the `MemoryAnalyzer.ini` file
    
2. change the default `-Xmx1024m` to a larger size
```



https://www.macat.vip/
####  如何关闭 iTerm2 中的自动换行？

**禁用换行:**

```
tput rmam
```

**启用换行:**

```
tput smam
```


1. Tabby


1. Iterm2
	1. 插件  [iterm2](obsidian://open?vault=%E5%B7%A5%E4%BD%9C&file=%E8%BD%AF%E4%BB%B6%2FmacOs%2Fiterm2 item2)
2. mvn 
		idea自带maven，只需要找到maven包的位置即可
		![[Pasted image 20240119100027.png]]
		将这句号写入~/.zshrc  
		 alias mvn='"/Applications/IntelliJ IDEA.app/Contents/plugins/maven/lib/maven3/bin/mvn"'
		 ![[Pasted image 20240119100250.png]]
		 
1. alfred
2. 截屏软件
	1. ishot pro
		1. ishot 会员就是 ishot pro
		2. shot pro是终身制的 ishot是订阅制的
		3. https://macmiao.lanzouj.com/ipuCm1kxzt0j
	2. shottr  免费  ocr智能识别英文
3. 超级右键
4. WPS
5. 百度网盘
6. Navicat Prenium
7. The Unarchiver
8. Office 全家桶
9. 超级右键专业版
10. Snipaste
11. obsidian
12. 贝锐向日葵
13. Total Finder
	1. 查看SIP是否关闭
		1. csrutil status
		2. 关闭教程： https://sspai.com/post/55066#!
	2. 下载地址： https://www.macat.vip/10413.html
14. yoink
	1. 下载地址: https://www.macat.vip/33447.html
15. 自带的 QuickTime Player
	1. 录屏操作  右键-> 新建屏幕录制 -> 选项进行设置 -> 录屏 -> 保存位置在选项中
		![[Pasted image 20240107225412.png]]
	2. 缺点： 文件生成大、智能全局录屏、生成的格式为mov
16. 录屏
	1. ishot pro
	2. kap
17. EV录屏 windows软件
18. dash 
	1. 下载地址: https://www.macat.vip/35010.html
	2. 交互: 与Alfred5 进行搜索![[Pasted image 20240107232059.png]]


macOs 软件免费下载  https://www.macat.vip/



链接: https://pan.baidu.com/s/1KTL4HrT1cZAru0-3eawJVA?pwd=h8ya 提取码: h8ya

![[Pasted image 20240103180242.png]]

![[Pasted image 20240103175816.png]]


![[../../壁纸/附件/Pasted image 20240415130542.png]]



##  Beyond Compare  这个授权密钥已被吊销

主要是解决beyond compare 在MAC重启后，不能使用的问题，报错：这个授权密钥已被吊销
https://blog.csdn.net/weixin_44719529/article/details/131852757
![[../../壁纸/附件/Pasted image 20240813142146.png]]
> cd '~/Library/Application Support/Beyond Compare'

2. 找到BCState.xml的文件，删除CheckID和LastChecked 
```
<CheckID Value="175022849020106"/> 
<LastChecked Value="2023-07-14 07:04:25"/>
```


3. 启动


javaClient jar包路径
```
/Users/gaotu/IdeaProjects/JavaProject/storm-earth-windows/storm-earth-windows-biz/target/storm-earth-windows-biz-0.0.1-SNAPSHOT.jar
/Users/gaotu/IdeaProjects/JavaProject/storm-earth-windows/storm-earth-windows-core/target/storm-earth-windows-core-0.0.1-SNAPSHOT.jar
/Users/gaotu/IdeaProjects/JavaProject/storm-earth-windows/storm-earth-windows-dispatch/target/storm-earth-windows-dispatch-0.0.1-SNAPSHOT.jar
/Users/gaotu/IdeaProjects/JavaProject/storm-earth-windows/storm-earth-windows-main/target/storm-earth-windows-main-0.0.1-SNAPSHOT.jar
/Users/gaotu/IdeaProjects/JavaProject/storm-earth-windows/storm-earth-windows-main/target/storm-earth-windows-main-0.0.1-SNAPSHOT-bin.zip
/Users/gaotu/IdeaProjects/JavaProject/storm-earth-windows/storm-earth-windows-server/target/storm-earth-windows-server-0.0.1-SNAPSHOT.jar
/Users/gaotu/IdeaProjects/JavaProject/storm-earth-windows/storm-earth-windows-util/target/storm-earth-windows-util-0.0.1-SNAPSHOT.jar
```