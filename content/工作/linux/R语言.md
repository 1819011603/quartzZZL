
下载
https://docs.posit.co/resources/install-r-source/

1. yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
2. yum-builddep R

RStudio





library(table1)


```
install.packages("sjPlot")

```



# Anaconda 安装R环境，安装Package和配置镜像，R语言Helloworld程序
https://blog.csdn.net/zpf336/article/details/104480732

PREFIX=/apps/home/rd/miniconda3

yum install libX11-devel
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --no-check-certificate
sh Miniconda3-latest-Linux-x86_64.sh
/root/miniconda3/bin/conda init
conda create -n R python=3.8
conda activate R
conda install r


echo 'export PATH="/apps/home/rd/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc 

默认不进入base环境
conda config --set auto_activate_base false



> `wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz`

>


阿里云主机:  https://ecs-workbench.aliyun.com/?spm=5176.ecscore_server.0.0.34884df5Er5HDr&form=EcsConsole&instanceType=ecs&regionId=cn-wulanchabu&instanceId=i-0jld0kb6049sx0wst0tx&resourceGroupId=&language=zh




###   r 安装源码包 安装本地r包本地安装r包安装报错

本地安装 直接去官方拿源码安装 快又便捷   选择对应系统的压缩文件


所有镜像地址： https://cran.r-project.org/mirrors.html


https://cran.r-project.org/web/packages/sjPlot/index.html

	镜像：  https://mirrors.pku.edu.cn/CRAN/web/packages/sjPlot/index.html
	
	更换为 https://cran.r-project.org/web/packages/包名/index.html


本地安装R包的命令
```
install.packages("/Users/gaotu/Downloads/jstable_1.3.0.tgz", repos = NULL, type="source")
```


####  错误: package or namespace load failed for ‘table1’ in loadNamespace(j <- i[[1L]], c(lib.loc, .libPaths()), versionCheck = vI[[j]]): 不存在叫‘Formula’这个名字的程辑包

这个错误表明在加载`table1`包时，出现了缺少名为`Formula`的依赖包或者命名空间。你可以尝试手动安装`Formula`包来解决这个问题。在R中，可以使用以下命令来安装`Formula`包：

R复制代码

`install.packages("Formula")`

安装完成后，尝试重新加载`table1`包，看看是否能够成功。如果还有其他依赖包缺失的话，也需要逐一安装这些依赖包。

希望这个建议对你有所帮助。如果你需要更多帮助，或者有其他问题，请随时告诉我。



### 三线表

```
mydata <= read.delim("/Users/gaotu/Documents/mydata.txt")
install.packages("table1")
library(table1)
units(mydata$Age) = "years"
units(mydata$BMI) = "kg/m<sup>2</sup>"
units(mydata$MET) = "min/week"
my_table <- table1(~ Sex + Age  + Ethnicity + BMI + `Smoking.status` + `Alcohol.drinking.status` +
                     +                        `Household.income` + Education + MET  + `Healthy.Diet.Score`+
                     +                        `Townsend.Deprivation.Index` + Employment | f.131742.0.0, data = mydata, topclass = 'Rtable1-zebra')
install.packages("htmltools")
my_table
```


#### p 值

pvalue <- function(x, ...) {
  # Construct vectors of data y, and groups (strata) g
  y <- unlist(x)
  g <- factor(rep(1:length(x), times=sapply(x, length)))
  if (is.numeric(y)) {
    # For numeric variables, perform Mann-Whitney U test.
    p <- wilcox.test(y, mu=0)$p.value  # 使用wilcox.test函数计算p值
  } else {
    # For categorical variables, perform a chi-squared test of independence
    p <- chisq.test(table(y, g))$p.value  # 使用chisq.test函数计算p值
  }
  # Format the p-value, using an HTML entity for the less-than sign.
  # The initial empty string places the output on the line below the variable label.
  # 在这里直接返回格式化后的p值
  return(sub("<", "&lt;", format.pval(p, digits=3, eps=0.001)))
}


table1(~Sex + Age  + Ethnicity + BMI + `Smoking status` + `Alcohol drinking status` +
+                  +            +            `Household income` + Education + MET  + `Healthy Diet Score`+
+                  +            +            `Townsend Deprivation Index` + Employment | f.131742.0.0, data = mydata, topclass = 'Rtable1-zebra', extra.col=list(`P-value`=pvalue), overall=F)