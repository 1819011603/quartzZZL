

下载[Darwin AMD64](https://github.com/git-lfs/git-lfs/releases/download/v3.0.2/git-lfs-darwin-amd64-v3.0.2.zip) 版本


要使用Git LFS跟踪大文件并上传它们，你需要执行以下步骤：

1. **在git目录初始化Git LFS：** 在你的Git仓库中，确保已经初始化了Git LFS。如果没有，可以在终端中执行以下命令：
    
    Copy code
    
    `git lfs install`
    
2. **配置要跟踪的文件：** 使用`git lfs track`命令来配置要跟踪的大文件。例如，如果要跟踪所有`.jpg`和`.png`格式的图片文件，可以执行以下命令：
    
    arduinoCopy code
    
    `git lfs track "*.jpg" git lfs track "*.png"`
    
    这将告诉Git LFS跟踪这些文件，并在推送时将它们上传到Git LFS服务器。

**如果有大文件已经add进来了  需要将暂存区还原**


 git reset --soft a42176cf2bd556f185520348ff3f9ecca4ae9c82
 git restore --staged . 
再重新add ，commit即可