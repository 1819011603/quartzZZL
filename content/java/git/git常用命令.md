
###  使用git config --global设置用户名和邮件


安装好git后，在命令行或终端中使用下面的命令可以设置git自己的名字和电子邮件。这是因为Git是分布式版本控制系统，所以，每个机器都必须自报家门：你的名字和Email地址。

```
git config --global user.name "bryan sun"
git config --global user.email "hitsjt@gmail.com"
```

> **注意git config命令的–global参数，用了这个参数，表示你这台机器上所有的Git仓库都会使用这个配置，当然也可以对某个仓库指定不同的用户名和Email地址。**
>  git config user.name="zhangzeling"
>  查看用户名  git config user.name


1. git branch 列出本地已经存在的分支，并且当前分支会用*标记
2. git branch -r 查看远程版本库的分支列表
3. git checkout -b 分支名   在本分支上创建分支 
4. git fetch和git pull的区别：
		![[Pasted image 20231223214455.png]]
5. 在使用`git push`之前，我们应该先设置好`origin`和`upstream`。
```shell
git push --set-upstream origin feature_branch
```
6. git fetch  当需要下载其他团队成员的更改时，就得使用`git fetch`。

## **git stash**

此git命令会临时存储已修改的文件。你可以使用以下Git命令处理stash工作
可以使用以下命令查看所有stash

```shell
git stash list
```

如果你需要应用stash到分支，那就使用`apply`

```shell
git stash pop
```

## **git log**
在`git log`的帮助下，你可以看到所有之前的提交，并且最近的提交出现在最前面。

用法

```text
git log
```

默认情况下，它将显示当前已检出分支的所有提交，但是你可以强制通过所有选项来查看所有分支的所有提交。

```text
git log --all
```


## **git rm**

有时你需要从代码库中删除文件，在这种情况下，可以使用`git rm`命令。

它可以从索引和工作目录中删除跟踪的文件。

用法

```text
git rm <your_file_name>
```


## **git clean**

你可以使用`git clean`命令处理未跟踪的文件。可以使用此命令从工作目录中删除所有未跟踪的文件。如果要处理跟踪的文件，则需要使用`git reset`命令。

用法

```text
git clean
```


git clean 从你的工作目录中删除所有**没有 tracked，没有被管理**过的文件。
太可怕，删除了就找不回了，一定要慎用。但是如果被 git add . 就不会被删除。
**git clean 和 git reset --hard 结合使用。**

```
clean 影响没有被 track 过的文件（清除未被 add 或被 commit 的本地修改）

reset 影响被 track 过的文件 （回退到上一个 commit）

所以需要 clean 来删除没有 track 过的文件，reset 删除被 track 过的文件

结合两命令 → 让你的工作目录**完全**回到一个指定的 <commit> 的状态
```


删除所有未跟踪的文件和目录：

```
git clean -fd
```


### git help
git 命令 --help 可以看到该条命令的帮助


### git rebase

git rebase详解（图解+最简单示例，一次就懂）
> https://blog.csdn.net/weixin_42310154/article/details/119004977


### 三、推荐使用场景

搞来搞去那么多，这其实是最重要的。不同公司，不同情况有不同使用场景，不过大部分情况推荐如下：

1. **拉公共分支最新代码——rebase**，也就是git pull -r或git pull --rebase。这样的好处很明显，提交记录会比较简洁。但有个缺点就是rebase以后我就不知道我的当前分支最早是从哪个分支拉出来的了，因为基底变了嘛，所以看个人需求了。**总体来说，即使是单机也不建议使用。**
2. **往公共分支上合代码——merge**。如果使用rebase，那么其他开发人员想看主分支的历史，就不是原来的历史了，历史已经被你篡改了。举个例子解释下，比如张三和李四从共同的节点拉出来开发，张三先开发完提交了两次然后merge上去了，李四后来开发完如果rebase上去（注意，李四需要切换到自己本地的主分支，假设先pull了张三的最新改动下来，然后执行<git rebase 李四的开发分支>，然后再git push到远端），则李四的新提交变成了张三的新提交的新基底，本来李四的提交是最新的，结果最新的提交显示反而是张三的，就乱套了，以后有问题就不好追溯了。
3. **正因如此，大部分公司其实会禁用rebase，不管是拉代码还是push代码统一都使用merge，虽然会多出无意义的一条提交记录“Merge … to …”，但至少能清楚地知道主线上谁合了的代码以及他们合代码的时间先后顺序**

##### 四、总结

无论是个人单机开发，还是公司协作开发，只要没有特殊需求，用merge准没错！！！





# git远程分支强制覆盖本地分支

> git pull --force origin test-2.2.0-ai:test-2.2.0-ai 



git pull --force <远程主机名> <远程分支名>:<本地分支名>


### 放弃当前跟踪的所有文件

git restore --staged .



###  如何自动设置远程跟踪分支



```
git config --global push.default current
```



#### git checkout .的时候 如果是新增的文件就去不掉

当你运行 `git checkout .` 命令时，它会丢弃工作目录中所有未暂存的更改。但是，如果有新增的文件（即尚未被 Git 跟踪），它们将不会被删除。

要删除新添加的文件，你可以使用 `git clean -f` 命令来清理工作目录中的未跟踪文件。请确保在执行此命令之前，你已经确认过这些文件是不需要的，因为这个操作是不可逆的。





> git checkout 远程分支

1. git fetch -p
2. git checkout orgin/远程分支名

`   git checkout origin/远程分支` 用于检出远程分支的本地引用，但此时不能进行编辑，只能查看远程分支的内容，主要用于查看远程分支的状态。




# Git revert 某次merge后再重新 merge代码被丢失(第一次想merge的代码再也merge不上了)

操作中: git revert 和  git reset的区别:

> 1. git revert是用一次新的commit来回滚之前的commit，git reset是直接删除指定的commit。
> 2. git reset 是把HEAD向后移动了一下，而git revert是HEAD继续前进，只是新的commit的内容和要revert的内容正好相反，能够抵消要被revert的内容。
> 3. 在回滚这一操作上看，效果差不多。但是在日后继续merge以前的老版本时有区别。因为git revert是用一次逆向的commit“中和”之前的提交，因此日后合并老的branch时，导致这部分改变不会再次出现，但是git reset是之间把某些commit在某个branch上删除，因而和老的branch再次merge时，这些被回滚的commit应该还会被引入。


#### 对 revert 的那次提交记录再次进行revert  (官方推荐方法)

```shell

git checkout master
# 从master拉一个新分支 revert_tmp
git checkout -b revert_tmp 
# 找到 revert 的那条提交记录，注意了，revert 相关的会有两条记录，第一条是 revert，第二条是 revert 后 merge 的记录，这里取第一条# 用revert_tmp分支revert之前的revert
git revert <版本号> 
#再用master分支合并此分支代码推到远程即可
#再将 之前的分支merge一下即可

git merge revert
git merge --continue

```




在使用Git进行版本控制时，如果你需要撤销一次merge操作并且之后再尝试重新merge，但发现代码无法重新merge上去，这通常是因为Git会记录已经合并过的提交，避免重复合并。这种情况可以通过以下步骤来解决：

### 1. 识别问题

首先，确认你当前的分支和你进行revert操作的commit：

```sh
git log --oneline
```

找到你revert的那个commit的哈希值。

### 2. 创建一个临时分支保存当前工作状态

在继续之前，最好创建一个临时分支来保存当前的工作状态，以防出现意外问题：

```sh
git checkout -b temp-branch
```

### 3. Revert the Revert

为了重新进行merge，你需要撤销之前的revert操作，Git中称之为“revert the revert”。

```sh
git revert <revert_commit_hash>
```

`<revert_commit_hash>`是你之前用来revert merge的commit的哈希值。这样做的目的是恢复merge前的状态。

### 4. 重新进行merge

现在你可以重新尝试进行merge操作：

```sh
git merge <branch_to_merge>
```

这样，你就可以重新合并之前的分支了。

### 5. 解决冲突

在merge过程中，可能会遇到冲突。你需要手动解决这些冲突，然后提交合并结果：

```sh
# 解决冲突后
git add .
git commit
```

### 6. 清理临时分支（可选）

如果一切顺利，合并完成后，可以删除临时分支：

```sh
git branch -d temp-branch
```






### 总结

整个过程的核心是使用“revert the revert”来恢复你撤销的merge，然后重新进行merge操作。这种方法可以确保你不会因为Git的merge tracking机制而丢失代码。

## git revert merge-commit-hash 就是单纯回滚这次的revert操作

是的,您总结得非常准确。`git revert <commit>`命令的作用就是单纯地撤销指定提交所做的修改,通过创建一个新的反向提交来实现。

具体来说:

1. `git revert`不会从Git仓库历史中移除或修改任何现有的提交记录。它只是在现有提交历史的基础上新增一个反向提交。
    
2. 该新的反向提交包含了完全相反的变更,目的是撤销并抵消之前提交所做的修改。
    
3. 该命令会保留所有提交历史,包括已撤销的那个提交,方便将来查阅和审计。
    
4. 执行该命令后,工作区的文件将回滚到撤销那个提交后的状态。
    
5. 如果你要撤销的是一次合并提交,那么revert将会试图以最小的代码变更来撤销合并时的所有文件变化。
    

所以`git revert`确实是一个非常干净利落的撤销操作,不会污染或破坏现有提交历史,只在历史记录上新增了一个反向提交。这一点非常不同于`git reset`这类有破坏性的撤销手段。

因此,您说`git revert`就是单纯地"滚回"上一次revert操作,准确地描述了它的本质 - 通过创建新提交来抵消之前的变更,从而实现代码修改的回滚。



### git log 和 git reflog有什么区别


假设你有如下的提交历史：

1. 你在分支上做了一些提交。
2. 然后你执行了 `git reset`，可能是 `git reset --hard` 或 `git reset --soft`。

在这种情况下，`git log` 不会显示被 `reset` 掉的提交，因为这些提交已不再是当前分支的一部分。然而，通过 `git reflog`，你可以看到所有这些操作，包括 `reset` 操作。


- `git log` 用于查看项目的变更历史。
- `git reflog` 主要用于恢复误操作，如找回删除的分支或提交。


总的来说，`git log` 更适合日常查看项目历史，而 `git reflog` 则是一个强大的恢复工具，可以帮助你找回误删的数据。


### 恢复误操作

如果你误用了 `git reset` 并且想要恢复到之前的状态，你可以使用 `git reflog` 查找到对应的提交哈希值并重置回来。例如：

```sh
$ git reflog
# 找到你想恢复的提交哈希，例如 HEAD@{2}

$ git reset --hard HEAD@{2}
# 或者
$ git checkout -b new-branch HEAD@{2}
```

通过这种方式，你可以恢复到任何之前的状态，即使这些状态在 `git log` 中不可见。



### git历史版本

![[../../壁纸/附件/Pasted image 20240727234052.png]]


### git 升级

查看 Git 版本
在终端中输入以下命令, 检查当前的版本
	git --version
升级 Git
	brew install git
重新链接 git
	brew unlink git && brew link git
关闭终端, 重新查看 Git 版本
	git --version




### git push到另一个仓库

 git remote remove origin

git remote add origin git@git.baijia.com:pandora/waliyun01/wly-log-record.git
