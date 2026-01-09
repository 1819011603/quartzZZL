
[多环境git 配置 - 掘金](https://juejin.cn/post/6951589523625082893)

> `ssh -T git@仓库服务器域名`

1. **自定义公钥匙名称**
    
    > ssh-keygen -f ~/.ssh/github_rsa -C "[181901160@qq.com](mailto:181901160@qq.com)"
	    ![[Pasted image 20240110010204.png]]
    
2. **github、gitlab 添加公钥**
    
    > 将 ~/.ssh/github_rsa 和 ~/.ssh/gitlab_rsa 公钥复制后添加到github和gitlab中。
    
3. **根据域名定义使用不同的密钥**
    
    我们要有多份密钥管理需要在对应文件夹下新建config 文件 **~/.ssh/config** 添加不同域名下使用的密钥
    
    ```python
    #git.baijia.com
      Host git.baijia.com
      HostName git.baijia.com
      User zhangzeling
      IdentityFile ~/.ssh/id_rsa
    
    #github
    Host github.com
      HostName github.com
      User 1819011603@qq.com
      IdentityFile ~/.ssh/github_rsa
    ```
    
4. git config
    
    我想为电脑上的不同项目设置不同的 git 用户信息配置，在 ~/.gitconfig 中添加配置如下：
    
    ```python
    [user]
    	name = zhangzeling
    	email = zhangzeling@baijia.com
    [includeIf "gitdir:/Users/gaotu/IdeaProjects/JavaProject/"]
        path = .gitconfig-work
    [includeIf "gitdir:/Users/gaotu/PycharmProjects/"]
        path = .gitconfig-self
    
    ```
    
    ![[Pasted image 20240110010240.png]]
    ![[Pasted image 20240110010249.png]]
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/cc4f3b2f-ab77-4a96-a9a8-570de1d5a11e/5b4018ac-2f4d-4c42-b373-f67644c430db/Untitled.png)
    
    ```python
    gaotu@gaotudeMacBook-Pro-8  ~  cat /Users/gaotu/PycharmProjects/.gitconfig-self
    [user]
    	name = 1819011603
    	email = 1819011603@qq.com
     gaotu@gaotudeMacBook-Pro-8  ~  cat /Users/gaotu/IdeaProjects/JavaProject/.gitconfig-work
    [user]
    	name = zhangzeling
    	email = zhangzeling@baijia.com
     gaotu@gaotudeMacBook-Pro-8  ~ 
    ```
    
5. 验证
    
    > ssh -T [git@baijia.com](mailto:git@baijia.com)
    
    > ssh -T [git@](mailto:git@baijia.com)[github.com](http://github.com)
    
![[Pasted image 20240110010337.png]]
    
![[Pasted image 20240110010350.png]]
    

gitLens 的使用

[Supercharge Your Git Workflow with the GitLens VS Code Extension](https://www.jamesqquick.com/blog/supercharge-your-git-workflow-with-the-gitlens-vs-code-extension/)