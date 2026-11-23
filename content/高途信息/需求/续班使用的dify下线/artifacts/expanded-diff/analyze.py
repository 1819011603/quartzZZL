import pathlib,json,difflib,hashlib,subprocess
out=pathlib.Path(__file__).parent; src=out.parent/'trace-recheck-20261123'
report=['# 两例精确差异与11文件审查','版本：部署91012878；TEST test-gtbg-dev-1；旧路径下游PROD。只读已有证据，不重新调用。verify/README不存在，实际读取verify.md。工作区当前并非需求分支，使用git对象读取，未切分支。','续班trace：15760243-f225-4246-a103-c9565c2652ba.0.3；退费trace：a32fe4b6-6269-4882-8d39-81c76f8ca23e.0.3。']
for case in ['renewal','refund']:
 a=json.loads((src/f'compare-{case}-prod-request.json').read_text());b=json.loads((src/f'compare-{case}-test-request.json').read_text()); raw=a['messages'][-1]['content']; head,tail=raw.split('  },\n  {\n    "role": "user",\n    "content": "',1); flat=[{'role':'system','content':head.split('"content": "',1)[1].removesuffix('"\n')},{'role':'user','content':tail.removesuffix('"\n  }\n]')}]
 for name,v in [('old-flat-decoded',flat),('new-messages',b['messages'])]: (out/f'{case}-{name}.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
 oldsystem='\n'.join(x['content'] for x in a['messages'][:-1])+ ('\n' if len(a['messages'])>1 else '')+flat[0]['content']
 for part,old,new in [('system',oldsystem,b['messages'][0]['content']),('user',flat[1]['content'],b['messages'][1]['content'])]:
  diff=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='old outer system + decoded flat system' if part=='system' else 'old decoded flat user',tofile='new actual '+part))
  (out/f'{case}-{part}.diff').write_text(diff or '# byte-for-byte identical\n')
  report.append(f'\n{case} {part}：相等={old==new}；字符数旧/新={len(old)}/{len(new)}；详见 {case}-{part}.diff。')
 report+=['\n|参数|旧实收|新实收|','|---|---|---|']
 for k in sorted(set(a)|set(b)):
  if k!='messages':report.append('|'+k+'|'+json.dumps(a.get(k,'<未传>'),ensure_ascii=False)+'|'+json.dumps(b.get(k,'<未传>'),ensure_ascii=False)+'|')
 report.append('messages：旧实际角色 '+str([m['role'] for m in a['messages']])+'；新实际角色 '+str([m['role'] for m in b['messages']])+'。旧flat内部role只是user文本，并非实际角色。')
repo='/Users/gaotu/IdeaProjects/JavaProject/student-data-refund-level'
diff=subprocess.check_output(['git','-C',repo,'diff','origin/release...91012878','--','*.java','*.xml'],text=True);(out/'code-11-files.diff').write_text(diff)
report.append('''
## 可复核提示词结论
续班：解码旧flat后system与user逐字符相等；实际请求从单user中的JSON文本变成system/user，去掉JSON包装与转义。不是请求相等，也不是采样造成的输入差异。
退费：旧真实system全文保留；旧flat system开头“退费根因分析”标签被新长system替代；后续输出字段约束保留并提升到真实system；user逐字符相等。具体删除/新增逐行见refund-system.diff。两个旧提示词中的非法JSON示例（未加引号、注释；退费额外大括号）也被保留，不是迁移新引入。
模型入口名称不同不能直接断言底层模型不同，需结合既存model-redirect-evidence.json；不得将未传参数解释成确定默认值。续班thinking已由主任务另行修正，本报告原请求是修正前快照，不作为当前配置。

## 响应质量：不是全部通过
- 续班旧侧写“不同用户”“部分用户”，新侧也写“不同用户”“部分用户”，违背不得总结为多个学员的意图；两侧都有，不可归因于迁移。均有commSummary与加粗，未见输入外主要事实，字数需用下方机器统计核实。
- 退费旧category=1-1，新=1-11，输入没有分类清单；新值恰是提示词示例。不能确认任一为合法业务分类，属于共同缺输入下的无依据编码风险，不是证明新模型更好/更差。coreReason=是、reasonJudgeType=1符合显式枚举，两侧communicateId=0、chatTime为空，不满足真实沟通ID与日期契约。新teacherWords“样本未提供老师应答原文。”不是老师原话。该例只覆盖最小生成，不覆盖业务可落值。
- 旧退费answer包含think标签；新answer纯JSON。直接JSON.parse旧完整answer失败，必须走既有提取；不能把推理文本当业务字段。是否所有实际后置插件正确处理须端到端验证。

## 11文件其余风险（静态判断，未作新的运行复现）
1. AiApplicationExecutor：显式prompt重载使用ofFlat，不注入gatewayCorePrompt。若退费应用经此入口迁移，会缺失Dify长system；需主Worker核对调用图及覆盖对象，未证明当前线上触发。
2. AiAgentAccessorOverride/Resolver：实际按agent粒度，多个application共享agent一起受影响，不能称单application回滚。overrideMap若配置JSON null可能NPE；platformType/model无完整性校验。属于配置边界风险。
3. LlmGatewayAccessor：extraParams只保护model/max_tokens/messages，允许stream=true；同步客户端随后按完整JSON解析，SSE会不兼容。建议约束stream=false或拒绝该键。现有样本未触发。length已有报错保护；其他异常finish_reason只warn是既有行为，不是新增回归。
4. AiModelCallOption：extraParams贯通，三项保留键不可覆盖；max_tokens不能靠params调节，需要命令/默认配置。SyncRequestTaskCommand：平台测试覆盖优先，但model仍优先Apollo；强制平台并不等于复刻所有旧配置。
5. DynamicPromptGenerator：非空gatewayCorePrompt替代原core而非追加；空值静默回退标签，迁移Dify托管system时可能静默丢指令。对必须迁移长system的应用应做前置完整性检查。
6. AiApplicationBO/AiApplication/AiApplicationMapper.xml：字段已贯通映射；Base_Column_List无条件读取新列，DDL必须先到位，即使未开开关仍依赖新列。未覆盖生产DDL现状，不在本轮读库范围。
7. AiApplicationTestServiceImpl：两次串行重新生成动态数据，不是冻结快照；本次user相等是证据，不能推广至其他样本。返回原始响应不能证明异步落值/业务插件枚举校验通过；createSyncRequestTaskCommandByName在try外，构造异常不会转ERROR。

## 覆盖与交付边界
已核对两例四份LiteLLM实收请求、两份双路响应、指定提交11文件diff；未调用业务、未改代码/Apollo/共享文档。未覆盖其他场景、重试、超时、长输入、分类合法性与落库，不替代主任务扩围验证。建议主Worker优先处理确证的样本验收口径，再按场景冻结数据检查枚举与事实忠实度；随机性要求多次结构统计，不要求文案字面相等。
''')
for case in ['renewal','refund']:
 d=next(iter(json.loads((src/f'compare-{case}.json').read_text())['data'].values()))
 for side,x in d.items():
  s=x['answer'].split('</think>')[-1].strip().removeprefix('```json').removesuffix('```').strip();v=json.loads(s)
  report.append(f'{case}/{side}：剥离既有think/围栏后JSON可解析；'+(f"commSummary长度={len(v['commSummary'])}（≤500）" if case=='renewal' else f"rationales数量={len(v['rationales'])}"))
(out/'report.md').write_text('\n'.join(report))
print('generated report and exact diffs',len(diff.splitlines()),'code diff lines')
