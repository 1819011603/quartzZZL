

#### git cherry-pick

![[../../壁纸/附件/Pasted image 20240204172218.png]]

#### 分支名称是有规范和含义的，不能乱取
fix feat
![[../../壁纸/附件/Pasted image 20240204171752.png]]



3. git stash pop 之后idea报错
	原因： 这是因为没有更新最新代码，在内存中还有一份旧的数据
	解决方法： 从磁盘重新导入项目  reload from disk![[Pasted image 20231222131728.png]]
###  2. 关于idea git中soft mixed hard keep的区别
![[Pasted image 20231223234702.png]]
https://www.cnblogs.com/w-wu/p/14675683.html

感谢分享，一般用soft，commit message不规范或者是邮箱不正确，都是这个。

Git有四种reset的模式：soft、mixed、hard、keep。  
  
1. Soft：重置HEAD但不改变索引区和工作区，适用于误提交（commit）了但是代码还需要保持修改状态的场景。  
  
2. Mixed：重置HEAD和索引区，但不改变工作区。并且这是默认的模式。适用于撤销上次提交，并且保持代码的修改状态（可以进行二次修改或者二次提交）。  
  
3. Hard：彻底重置。重置HEAD、索引区和工作区。慎用。主要用于上次提交的代码全部不需要。  
  
4. Keep：重置HEAD，使得未跟踪的文件保持不变。主要用于丢弃最后的提交，但是对于没有添加追踪的文件不作影响。这个对于在错误的分支上工作的修复效果很好 (如果你忘记了该在哪个分支上进行开发)。  
  
Keep也可以理解为，在硬重置（Hard）和混合重置（Mixed）之间的一种方式。他会保留那些在你打算丢弃的提交中明确修改过的文件，防止你丢失工作。#### 


`git reset`命令主要用于撤销Git的某些操作，可以理解为“回滚”。在执行`git reset`命令时，可以使用`--soft`, `--mixed`, `--hard`, `--keep`选项来指定Git应如何处理工作目录和暂存区。  
  
例如：  
- 如果你想撤销上次的commit，但希望保留已经暂存和修改的文件，那么你可能会使用`git reset --soft HEAD~1`。  
- 如果你想撤销包括暂存在内的所有操作，但仍然保留修改的文件，你可能会使用`git reset --mixed HEAD~1`。  
- 如果你想完全撤销所有操作，包括工作目录中的修改，你可能会使用`git reset --hard HEAD~1`。  
- 如果你在错误的分支上工作并提交了代码，那么你可能希望回滚这个commit，但保留那些新建的（Git中的"未跟踪"）文件，这时你可能会使用`git reset --keep HEAD~1`。  
  
`--soft`, `--mixed`, `--hard`, `--keep`这些选项并不会影响Git的版本历史，它们只是指定了在回滚的同时，Git应如何处理工作目录和暂存区。因此，它们的用途取决于你想如何管理这些更改。


### 3. idea中git commit 的时候出现 you are about to commit crlf line separators to the git repository...
![[Pasted image 20231224000620.png]]

这个提示表明你正在将包含CRLF（Carriage Return Line Feed，即\r\n）行结束符的文件提交到Git仓库。  
  
Git有一个名为`core.autocrlf`的配置选项，用于控制如何处理行结束符。它有三个可选值：`true`，`input`和`false`。  
  
- 如果设置为`true`，当你检出（checkout）代码时，Git会将行结束符从LF转换为CRLF，当你提交代码时，Git会将行结束符从CRLF转换为LF。  
  
- 如果设置为`input`，当你提交代码时，Git会将行结束符从CRLF转换为LF，但在检出代码时不会进行转换。  
  
- 如果设置为`false`，Git不会进行任何转换。  
  
回到你的问题，出现这个提示通常是因为你的`core.autocrlf`设置为`input`或`false`。如果你想让Git自动处理行结束符，你可以将`core.autocrlf`设置为`true`。在命令行中，你可以使用以下命令来实现：  
  
```  
git config --global core.autocrlf true  
```  
  
此外，你也可以在IDEA中进行设置。在设置菜单中，依次选择`Version Control` -> `Git`，然后在`Line separator conversion`下拉框中选择`CONVERT_TO_COMMIT_EOL`。  
  
如果你确保你想提交包含CRLF的文件，你可以忽略这个提示并继续提交。


### 4.当 git 命令无法显示/处理中文命名的文件时

> git config --global core.quotepath false

这个命令是设置 git 的一个全局配置，core.quotepath 设置为 false 表示 git 不再输出八进制填充的文件名，而是允许输出非 ASCII 的文件名。这样你创建或查看的中文命名的文件就可以在 git 命令中被正确处理和显示了。

这个设置是全局性的，也就是只需要设置一次，以后在你的计算机上使用 git 时都会按照这个设置来输出文件名。


### 5. git 更换国内镜像源

```shell
cd "$(brew --repo)"
git remote set-url origin git://mirrors.ustc.edu.cn/brew.git
cd "$(brew --repo)/Library/Taps/homebrew/homebrew-core"
git remote set-url origin git://mirrors.ustc.edu.cn/homebrew-core.git
```




#### idea gitlab使用token无法登录

![[../../壁纸/附件/Pasted image 20240820105343.png]]

使用这个登录

siirsH6nGRQLQpoYHF8a


解决思路:

禁用内置插件 gitlab



### 在开发过程中 使用git 拉取master代码创建一个分支A 开发一部分后 A分支合并了master分支准备上线 但是在A分支上使用git reset --soft将A分支的提交统一弄成一个分支后提交 后面master分支又有改动 master分支合并A分支代码有遗漏 是ABA的问题吗

1. **分支操作流程**
    
    - 你从 `master` 创建了 `A` 分支。
    - 在 `A` 分支上开发并合并了 `master` 的改动。
    - 通过 `git reset --soft` 将多个提交压缩成一个新的提交后重新提交。
2. **`git reset --soft` 的影响**
    
    - `git reset --soft` 会将 `A` 分支的历史提交重写，并将所有的更改放入暂存区，生成新的提交。
    - 由于 `A` 分支的提交历史被重写，Git 会认为新的提交与之前的提交是完全不同的，即使代码内容相同。
3. **主分支新增改动后再次合并的情况**
    
    - 如果 `master` 分支在合并 `A` 分支后又有新改动，然后再次合并 `A` 分支（或 `A` 分支先合并 `master` 的改动），Git 可能会因为提交历史的变化而无法正确识别已经合并的代码，导致部分变更被遗漏。


### **为什么这不是严格的 ABA 问题？**

- **ABA 问题的定义**：在并发或分布式系统中，某个线程在检查一个值是 `A` 时，另一个线程将值变为 `B`，然后又恢复为 `A`。第一个线程无法感知这种变化，导致逻辑错误。
- **Git 的问题本质**：这里的问题不是因为 Git 未能感知到状态的变化，而是由于分支提交历史被重写（通过 `reset` 操作）后，Git 的合并算法基于提交历史而非代码内容对比，导致遗漏。



### **如何避免此类问题？**

1. **避免在合并后使用 `git reset --soft` 重写历史**
    
    - 合并分支后，尽量不要对已经合并的提交历史做修改（如 `reset`、`rebase` 等操作），以避免 Git 的提交历史混乱。
    - 如果需要压缩提交，应在分支合并前完成（即在 `A` 分支开发阶段完成）。