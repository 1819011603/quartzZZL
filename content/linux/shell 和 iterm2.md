
1. 历史记录
	1. 在iterm2中使用  ctrl + R， 可以搜索
	2. history | grep 也可以搜索
2. 撤销操作
			清屏1：command + r
			 清屏2：ctrl + k
			- 垂直分屏：command + d
			- 水平分屏：command + shift + d
			- 切换屏幕：command + option + 方向键
			- 查看剪贴板历史：command + shift + h
			- - `Ctrl + -` – 撤销操作。
				- ![[Pasted image 20240110142220.png]]
				- 新增加 Command+Z 设置撤销操作
					![[Pasted image 20240110142344.png]]
3. # mac 系统 iTerm2 按单词前进、后退、删除 https://blog.csdn.net/JackLang/article/details/116330286
	- 点击 Keyboard Shortcut 时会录制你的操作（即此时需要同时按 ⌥ 和 ← ）
	- Action 选择 “Send Escape Sequence”
	- Esc+ 填入 “b”
4. # iterm2（zsh）粘贴慢解决办法 https://blog.csdn.net/lxyoucan/article/details/123072528
	1. 我在[macOS](https://so.csdn.net/so/search?q=macOS&spm=1001.2101.3001.7020)环境中使用的是iterm2终端，每次在粘贴大量命令的时间，明显感觉粘贴速度慢。就感觉粘贴也是一个字一个字粘贴的。在命令过长时由为明显。
	2. 本以为是[iterm2](https://so.csdn.net/so/search?q=iterm2&spm=1001.2101.3001.7020)的原因，后来发现原来是因为zsh的原因导致的。


要在 Linux 中开启一个子进程并立即返回，您可以使用 `&` 符号，或者使用 `nohup` 命令。这两种方法都可以使命令在后台运行，且终端会立即返回可输入状态。
```
nohup your_command &

nohup python -u  工作机-语音记录刷入.py &>nohup.out 2>&1 &

```
```
your_command &
```


### nohup

解决nohup不能及时打印python print日志

nohup.out中显示不出来[python](https://so.csdn.net/so/search?q=python&spm=1001.2101.3001.7020)程序中print的东西，这是因为python的输出有缓冲，导致nohup.out并不能够马上看到输出。


python 有个-u参数，使得python不启用缓冲。

```
nohup python -u  工作机-语音记录刷入.py &>nohup.out 2>&1 &
nohup python -u  工作机-语音记录刷入.py &>nohup.out >&1 &
```




**查看当前目录下所有子目录的大小**：
```
du -h
```

**查看目录下每个文件或目录的大小**：
```
du -ah /path/to/directory
```


> 查看进程运行时间

`ps -p <PID> -o etime`