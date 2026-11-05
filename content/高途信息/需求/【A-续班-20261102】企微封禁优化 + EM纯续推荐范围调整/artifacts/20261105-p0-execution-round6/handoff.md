# W1 TEST执行安全交接（round6）

2026-11-05；task_type=requirement；任务243aa61a/工作单57b56e168cd2，attempt9。运行时自动80%交接要求收束本会话，不是所有者业务暂停。Boss已解除上一轮临时只读限制，TEST最小样本与对应业务执行授权继续有效；新会话先查在途和子任务终态后按原工作单续接，不重新索权。

## 本轮已完成

- 原502诊断沿用：失败在argparse解析--publish之前，旧build零业务写入；原计划骨架588858850300473344复用，未再次clone。
- 本轮17:35:44提交移除publish的异步build，run r-20261105173544-ff5255cd，15,308ms后ok，published=true。已另行回读实际对象和关系，不把ok当可用。
- 已核当前TEST/test-gtbg-dev-3：product-b 07ba05df/IP10.218.248.248；cart a34016fd/IP10.218.237.47；order 0cc8ef68/IP10.218.236.236；order-b 0cc8ef68/IP10.218.237.111，均Running/UP。镜像及完整pod见versions.json。
- 当前计划数据库status=2/is_test_data=1/isdel=0，名称W1-P0-243aa61a-EM独立主计划；不是先前status0骨架状态。绑定行69854（number588861421939404800）将前课588861395571990528绑定到该计划；读后置关系确认指向后课588861400563212288、calculateRenewalType1、grade15/subject5/2026/X。
- 新前课588861395571990528，B测试-五年级语文春季前置B；班588861397654462464，业务号15YW26C6M111001，price0。
- 新后课588861400563212288，B测试-五年级语文暑假后置1B；班588861402658267136，业务号15YW26XTRO11001，price100分。两课均来自本次clone后build，科目语文/grade15；前2026/C、后2026/X。

## 未得到可用样本及真实失败

**造数没有完成可用门槛。**safe-readback.json确认两班publishStatus0、saleStatus0、teacherList=[]；最初独立回读两侧subclazz均[]。前班get_lesson_detail显示clazzLessonIsExist=false、clazzLessonCountDesc0、vsn0，lessonList只有待排占位行（number/teacherNumber/beginTime/endTime全空），不是实际课节。

本Worker临时编排误把非空lessonList当成已有真实课节，跳过排课后提交clazz_publish，被code1“大班课必须有课节后才可以发布!”拒绝。repair-built-classes.json只有get_lesson_detail和clazz_publish两步，没有create_lesson、create_subclazz，也没有操作后班；没有成功发布的证据，不能写成平台/业务功能已修好。

接手应修正临时编排的前置判据（clazzLessonIsExist及有number/时间/老师的真实课节），用既有outline/选老师/创建课节/发布班级/挂辅导班能力补齐**现有班级**，不要重新build或重建课程。可复用待排占位的前课outline588861396261953536；先独立读当前版本和是否已有人排课，后班outline另读。临时脚本/模板来源见/tmp/w1-p0-243aa61a/round6/repair-built-classes.py和工具core/workflow_runner.py create_lesson_simple。仅修临时测试编排，不修改造数平台或业务代码。

后置关系接口clazzTotal0，与未发布班级相符；它不能证明课程没有班级行。当前没有order/prepare可售检查成功、没有新订单/支付、没有资格数据或推荐场景通过。未购/隔离/碰撞等仍未执行。

## 测试状态保留与安全现场

- 保留本轮专用计划、前后课程/班级及绑定供续接；没有删除/回滚这些新建对象。下一次先查询以上精确ID，不重新clone/build。
- 所有父Worker命令均已退出。异步build已经终态ok，未留后台造数run；修补脚本已因发布失败结束。安全回读已成功，第一次因本地qa .venv无mcp依赖在import阶段退出未发起业务调用，改mcp-servers venv完成只读查询。
- 企微子任务W1-e4187e（generation2）result-8已完成安全交接，父子任务均无在途业务操作。代课申请project3/4均code0，但TEST接口和真实页面实际身份仍gongxuemeng（177071），不称切换成功；两项目均已退出，恢复回读code0，trace 020d8c35-35c3-4a6d-a9e0-528ba2dc7f3a.0.3。原全局代课列表未快照，仅确认本轮两申请退出及TEST身份与基线一致。未新增企微对象、好友/标签/备注/DB/ES业务写入或待恢复业务状态。详见qiwei-handoff.md、qiwei-results.json和child-result8-receipt.json。
- 实际大班续班服务页面tab34可见添加标签、修改企微备注入口和16行；未选择学员、未提交。页面班名尚未和真实班级ID网络映射，不据此嫁接历史对象。浏览器标签页保留，无未提交弹窗或在途任务，共享Chrome服务未关闭。P0-10/11只证入口可见，P0-12未执行。尚无新增已确认必须人工介入的阻塞。
- 本轮专用计划及两班已登记既有fixture库：plan:588858850300473344（可用性unknown），clazz:588861397654462464及clazz:588861402658267136（not_sellable），owner W1/task243aa61a，TEST/test-gtbg-dev-3。注册回执及先前实际list回读确认三对象，见fixture-registration.json；登记不等于业务可用。保留续接，未清理。
- 父Workerorder-baseline.json：两新课程对候选7658129872/7489648821无旧order_info命中；7658129872已有旧A前/后订单。小班order_item查询字段order_number不存在，是查询脚本字段错，不是业务失败；后续按实际number/sku字段核对，不把该失败当未购买证据。

## 原完整工作单仍待完成

1. 准备EM可售/可用最小对象并独立回读，构成真实隔离、碰撞、无从在读/仅主资格、可售未购、不同学年学期等关系，再执行对应P0-03至09尚缺步骤；不得以原计划内重绑替代跨计划反例。仅前后课期不同不等于已构成主从学期隔离。
2. 合并企微子任务实际结果与恢复；继续P0-10/11/12未覆盖项。cosplay尚未确认成功不等于必须人工；只有无法取得受控真实官方好友与原备注时才按已列最小条件请求帮助。
3. 使用lark-doc写回原P0并回读，按25项契约→原30条→12卡→样本步骤→结果证据逐点核对；信息完整性和业务通过数分别统计。
4. P0本轮尚未改写，最后有效回读仍revision159；分类基线12卡完整1/准备1/缺10，原30条完整2/准备10/缺18，尚不能因build ok提升分类或通过数。未覆盖页面/新下单/回溯不说通过。

## 既有交付继续复用

P0 https://gaotuedu.feishu.cn/wiki/KeCZwdJTBiIJDJkX8lRcGb9gnCs，docx ZQUXdlDxWoknJhxu914c2uVYnBr。此前25契约、30条映射、12卡36步及证据包/链接校验继续有效；原MR1528仅静态比较，不合并，其createTime圈班不能替代min(begin_time)。

专用P0 skill=banshan-case；源/安装的SKILL.md和references/doc-templates.md已更新且校验通过，本轮不重跑：
/Users/gaotu/bridge/payload/skills-cold/banshan-case/SKILL.md
/Users/gaotu/bridge/payload/skills-cold/banshan-case/references/doc-templates.md
/Users/gaotu/.claude/skills-cold/banshan-case/SKILL.md
/Users/gaotu/.claude/skills-cold/banshan-case/references/doc-templates.md

禁止前后端业务代码修改、服务部署、生产写入、对外联系；测试造数/业务操作只限受控TEST对象。自动上下文交接绝不记为所有者业务暂停。

## 最终交接回读

已接收并整合result-8终态；主子任务没有在途业务请求、造数run、备注任务或待恢复业务写入。父build已终态；本地失败脚本已退出。保留的仅为明确登记的TEST计划/课程/班级/绑定以及只读浏览器页。新worker继续原授权前先核这些精确ID当前状态，再从缺失的真实课节/老师等准备步骤续接，不重复整批build；企微复用同一子任务会话。当前外部P0仍revision159，未写本轮结果。
