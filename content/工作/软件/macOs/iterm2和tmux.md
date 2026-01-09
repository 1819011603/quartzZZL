



# iTerm2 + Oh My Zsh 打造舒适终端体验

https://github.com/sirius1024/iterm2-with-oh-my-zsh

有同学说补全命令的字体不太清晰，与背景颜色太过相近，其实可以自己调整一下字体颜色。

Preferences -> Profiles -> Colors 中有Foreground是标准字体颜色，ANSI Colors中Bright的第一个是补全的字体颜色。
![[../../壁纸/附件/ziji.itermcolors]]
### fzf-tab  插件


Fzf 是一个模糊匹配查找器，可与 zsh 完美配合。通过 key-binding 或使用 fzf-tab 插件实现命令或目录的补全。

让我们开始安装。

首先，这个插件要在 zshrc 的最后加载。因此，我们无法用 oh-my-zsh 来管理这个插件。

插件下载，将其 clone 到 `~/.config/zsh`，命令如下：

```bash
git clone https://github.com/Aloxaf/fzf-tab ~/.config/zsh/fzf-tab/
```

```bash
echo 'source ~/.config/zsh/fzf-tab/fzf-tab.plugin.zsh' >> ~/.zshrc
```


```bash
source ~/.zshrc
```





# tmux
https://cloud.tencent.com/developer/article/1526675

键入 `tmux` 命令，就进入了 Tmux 窗口。
上面命令会启动 Tmux 窗口，底部有一个状态栏。状态栏的左侧是窗口信息（编号和名称），右侧是系统信息。

显式输入 `exit` 命令，就可以退出 Tmux 窗口。

#### **2.3 前缀键**

Tmux 窗口有大量的快捷键。所有快捷键都要通过前缀键唤起。默认的前缀键是 `Ctrl+b`，即先按下 `Ctrl+b`，快捷键才会生效。

举例来说，帮助命令的快捷键是 `Ctrl+b ?`。它的用法是，在 Tmux 窗口中，先按下 `Ctrl+b`，再按下 `?`，就会显示帮助信息。

然后，按下 `ESC` 键或 `q` 键，就可以退出帮助。


#### **3.1 新建会话**

第一个启动的 Tmux 窗口，编号是 0，第二个窗口的编号是 1，以此类推。这些窗口对应的会话，就是 0 号会话、1 号会话。

使用编号区分会话，不太直观，更好的方法是为会话起名。

```javascript
$ tmux new -s <session-name>
```

复制

上面命令新建一个指定名称的会话。

#### **3.2 分离会话**

在 Tmux 窗口中，按下 `Ctrl+b d` 或者输入 `tmux detach` 命令，就会将当前会话与窗口分离。

```javascript
$ tmux detach
```

复制

上面命令执行后，就会退出当前 Tmux 窗口，但是会话和里面的进程仍然在后台运行。

`tmux ls` 命令可以查看当前所有的 Tmux 会话。



**系统操作**

```text
?	列出所有快捷键；按q返回
d	脱离当前会话；这样可以暂时返回Shell界面，输入tmux attach能够重新进入之前的会话
D	选择要脱离的会话；在同时开启了多个会话时使用
Ctrl+z	挂起当前会话
r	强制重绘未脱离的会话
s	选择并切换会话；在同时开启了多个会话时使用
:	进入命令行模式；此时可以输入支持的命令，例如kill-server可以关闭服务器
[	进入复制模式；此时的操作与vi/emacs相同，按q/Esc退出
~	列出提示信息缓存；其中包含了之前tmux返回的各种提示信息
```

**窗口操作**

```text
c	创建新窗口
&	关闭当前窗口
数字键	切换至指定窗口
p	切换至上一窗口
n	切换至下一窗口
l	在前后两个窗口间互相切换
w	通过窗口列表切换窗口
,	重命名当前窗口；这样便于识别
.	修改当前窗口编号；相当于窗口重新排序
f	在所有窗口中查找指定文本
```

**面板操作**

```text
”	        将当前面板平分为上下两块
%	        将当前面板平分为左右两块
x	        关闭当前面板
!	        将当前面板置于新窗口；即新建一个窗口，其中仅包含当前面板
Ctrl+方向键	以1个单元格为单位移动边缘以调整当前面板大小
Alt+方向键	以5个单元格为单位移动边缘以调整当前面板大小
Space	        在预置的面板布局中循环切换；依次包括even-horizontal、even-vertical、main-horizontal、main-vertical、tiled
q	        显示面板编号
o	        在当前窗口中选择下一面板
方向键	        移动光标以选择面板
{	        向前置换当前面板
}	        向后置换当前面板
Alt+o	        逆时针旋转当前窗口的面板
Ctrl+o	        顺时针旋转当前窗口的面板
```


tmux clock命令（或者ctrl + b + t键盘快捷键）显示一个时钟，点击任意按键退出时钟
	![[../../壁纸/附件/Pasted image 20240123152352.png]]


`set -g mouse on` 是tmux的命令之一，它用于启用鼠标支持。启用后，你可以在tmux窗格之间滚动、选择和点击操作。这个功能对于那些更习惯使用鼠标进行操作的用户来说可能会更加方便。


####  装了tmux默认鼠标滚动是切换输入命令而不是滚动页面 如何解决

- 第一种方案-Session生效

先按Ctrl+b, 然后输入":set mouse on"

- 第二种方案，配置文件

echo "set -g mouse on" >> ~/.tmux.conf

接着，用 `tmux source-file ~/.tmux.conf` 命令使其生效。