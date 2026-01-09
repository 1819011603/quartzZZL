
1. 超过100M，将文件从 Git 跟踪中移除，可以按照以下步骤进行操作：
	1. git rm --cached test/ukb_all.txt
2. 使用 "git restore <文件>..." 丢弃工作区的改动
3. 固定将某些文件不加入git
	1. 编写.gitignore
		![[Pasted image 20240110134405.png]]
	