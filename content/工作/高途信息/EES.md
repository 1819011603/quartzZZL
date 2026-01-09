
Engagement and Efficiency System 教学服务效率系统。通过服务二讲，给二讲的工作提效来辅助二讲更好的服务学员。

● 服务工作台：[https://fuwu.baijia.com/](https://fuwu.baijia.com/)实际上是广义上的二讲的服务工作台，包含长期班二讲（一般简称二讲）和短期班二讲（一般简称顾问）。

● EES：可以通过[https://ees.baijia.com](https://ees.baijia.com/)访问到，实际上也是跳转到服务工作台（[https://fuwu.baijia.com/](https://fuwu.baijia.com/)）为了更好的区分是给二讲服务还是给顾问服务，我们一般会把给二讲服务的叫做EES系统，实际是同一个服务工作台系统，通过权限差异化给二讲用的叫EES，给顾问用的叫CRM。

● CRM：可以通过[https://crm.baijia.com](https://ees.baijia.com/)访问到，实际上也是跳转到服务工作台（[https://fuwu.baijia.com/](https://fuwu.baijia.com/)）为了更好的区分是给二讲服务还是给顾问服务，我们一般会把给顾问服务的叫做CRM系统，实际是同一个服务工作台系统，通过权限差异化给二讲用的叫EES，给顾问用的叫CRM。


EES 学员部分文档  
https://docs.baijia.com/doc/DQXpraGxSTkZTYVlj


服务工作台操作指南
https://docs.baijia.com/doc/DQUZCUHJQd0dRSkdR


李君分享 https://docs.baijia.com/doc/DQVBJTWRPVGxjcXBFcWNDR3JS


https://test-fuwu.baijia.com/crm/microFairy/tutoringClassManage


辅导工作台EES-新人熟悉: https://wiki.baijia.com/pages/viewpage.action?pageId=312626771

  EES入门
https://docs.baijia.com/doc/DQWl0UmZNcGpPSUxtT3dBWlFM

想快速了解 EES 可以看这个文档 https://doc.baijia.com/docs/A15xvB7wQ7zns8ew


服务名称


student-center  
student-data


https://wiki.baijia.com/pages/viewpage.action?pageId=273119761  
高达立项文档



辅导班列表: https://test-fuwu.baijia.com/bgwApi/distribution-management/subclazz/management/listSubclazzAggInfo


课节管理: https://test-fuwu.baijia.com/bgwApi/component/student-center/clazz/lesson/formal/list
com.gaotu.yunying.student.center.web.api.SubclazzLessonController#listClazzFormalLesson

![[../壁纸/附件/Pasted image 20241220165332.png]]


查询课节下的学员(课节学员列表): https://test-fuwu.baijia.com/bgwApi/component/student-center/lesson/user/list

clazzLessonNumber课节  clazzNumber班级 subclazzNumber辅导班
```
根据辅导班去查班级 就是前端没有传过来clazzNumber, 使用查询的班级id, 否则使用前端传递过来的
查询班级信息 课节信息
获取顾问, 二讲, 主讲老师的信息(顾问和二讲里面优先顾问)


根据辅导班编号分页查询学员在班记录（滚动id）
```

![[../壁纸/附件/Pasted image 20241223110045.png]]
比如这是大班课的班课模型，课程下会有多个班级，每个班级下面会有多个辅导班，那么辅导班就是二讲老师服务的单元。一般一个周期之内服务一个辅导班，特殊情况也可能带多个班级。



one -> one  周期长
topic  纪要 代办




企微接入自建应用: https://blog.csdn.net/zxy19931069161/article/details/132720957
企微主体侧边栏沟通
https://wecom-sidebar.github.io/wecom-sidebar-docs/

https://cloud.tencent.com/developer/article/1967855
公司文档: https://docs.baijia.com/doc/DQVZrd3lOeVFNVE5oR0puZ2Vq


二讲或者顾问的权限才行

GET /crmApp/scrm/wk/auth/account?code=1fIwqnygKFxFICumARL_matcZCmtEyzbo9bTcsSlloE&corpId=ww5d80967f90ceb8cb&appId=1000034 HTTP/1.1
获取高途用户信息


https://sales-crm.gaotu.cn/crmApp/scrm/wk/user/getByExternalUserId?externalUserId=wmngwXDwAAVH5ifjPWfOIqrjT97kjlnQ&corpId=ww5d80967f90ceb8cb
获取外部联系人信息

![[../壁纸/附件/Pasted image 20241224104926.png]]

交接文档：https://wiki.baijia.com/pages/viewpage.action?pageId=269668169  
https://doc.baijia.com/docs/kBEXadGzPnOlFRgL  
https://docs.baijia.com/doc/DQXVOcm5FZW11U2NicHhRdGZQ  
https://docs.baijia.com/doc/DQVZrd3lOeVFNVE5oR0puZ2Vq


```

但是并不是所有对话（session）都能打开这个侧边栏的，只有在 **外部联系人** 和 **外部联系群** 的对话中才能右下角打开侧栏的按钮。

那 **外部联系人** 和 **外部联系群** 又是个啥？为什么只有在这种情况下才能打开呢？这就要说到侧栏到底要解决的什么问题。

侧栏真正要解决的痛点其实是 **社群/客户运营和管理**。

而且销售人员主要的工作就是要精细化运营、每天都要和客户以及群聊 **聊天**。什么时候聊、怎么聊、聊什么都是大学问，而且一旦和这么多客户、群聊聊天更是难上加难。类比一下，时间管理大师最多也只能和 10 个人聊也已经顶天了。

所以企业微信就想：能不能在聊天会话当中有一个工具箱，销售人员就可以在这个工具箱里查看客户/群聊的业务数组，或者通过这个工具箱更好地运营。这就是侧边栏的由来。

上面的这些 “客户” 和 “群聊” 则被称为：**外部联系人** 和 **外部联系群**，这里的 “外部” 指的就是 **不是自己企业内部员工**。

侧边栏本质上也是一个 WebView，所以我们只需要写好前端，无论是普通 html 或者 SPA App 都能被放在侧边栏上。

但是普通的前端还是不够的，如果你想和 **企业微信** 进行一定的交互，比如发消息、立即创建群聊、打开个人信息弹窗，那就需要企业微信提供的 JS-SDK，具体文档请看这里。


```

![[../壁纸/附件/Pasted image 20241220181031.png]]

企微的服务端已经由企业微信提供了，那我们要实现的就是 **侧边栏** 和 **业务服务端** 了。如果你是第一次搞侧边栏，一定会被弄得非常烦，所以建议 Fork 我的 侧边栏（前端）模板 和 后端模板，然后在这基础上进行修改。


这种 userId 的获取机制和微信网页开发是差不多的，需要先重定向某个 url，然后从 `search` 参数获取 `code`，再用这个 `code` 通过上面的转发服务向企业微信服务端换取 `userId`，具体实现可以看 文档这里。

![[../壁纸/附件/Pasted image 20241220181144.png]]





```

  
/**  
 * 班级编号  
 */  
private Long clazzNumber;

/**  
 * 辅导班编号  
 */  
private Long subclazzNumber;


/**  
 * 课节编号  
 */  
private Long clazzLessonNumber;



```





性能优化: 


服务总线程数大概1000



指标并行时  最大线程数不够

```
com.gaotu.student.data.client.data.DataHelperV2#parallelQueryWithoutException(java.util.List<T>, com.gaotu.student.data.client.data.model.DataContext, java.lang.Class<T>)



com.gaotu.student.data.config.ExecutorsPoolConfig#dataQueryThreadPool


```
