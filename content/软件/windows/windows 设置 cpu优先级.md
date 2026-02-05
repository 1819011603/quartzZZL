
搜索 windows工具 -> 注册表编辑器


```

HKEY_LOCAL_MACHINE\SOFTWARE\sofMicrosoft\Windows NT\CurrentVersion\Image File Execution Options 
您可以简单地将上面的地址复制并粘贴到注册表编辑器的地址栏中到达该文件夹。

1.创建程序名称的文件夹
2.在程序名称文件夹创建 PerfOptions 文件夹 
3.在PerfOptions 文件夹右键新建DWORD（32）名称为 CpuPriorityClass 
双击 CpuPriorityClass 输入所需的CPU优先级的值： 1 =空闲。 2 =正常(默认)。 3 = 高 (强烈建议)。 4 =实时(如果客户端开始暂停，将导致瓶颈)。 5 =低于正常。 6 = 高于正常值
```

![[Pasted image 20250629233428.png]]
修改完后退出注册表（一定要退出才生效）， 重启应用后生效




软件名称可以直接在任务管理器上看
![[Pasted image 20250629233403.png]]