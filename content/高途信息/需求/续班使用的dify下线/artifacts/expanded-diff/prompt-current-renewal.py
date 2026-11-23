import pathlib,json,difflib
out=pathlib.Path(__file__).parent;p=out.parent
load=lambda x:json.loads((p/x).read_text())
cases=[('画像','expanded-renewal/profile-prod-received.json','expanded-renewal/profile-test-received.json','2a9ff650-ba6f-4bf2-93f8-88034f864c93.0.3','2a9ff650-ba6f-4bf2-93f8-88034f864c93.0.3'),('摘要','trace-recheck-20261123/compare-renewal-prod-request.json','trace-recheck-20261123/dify-thinking-verified.json','15760243-f225-4246-a103-c9565c2652ba.0.3','f059219f-2d7c-46c5-945e-fd3a9cdab509.0.3'),('分层','expanded-renewal/tier-valid-prod-received.json','expanded-renewal/thinking-received.json','3c9e6b70-e6f3-4f95-883b-14408cdafc2b.0.3','7a05052d-9094-4a00-aa88-bf44dcf0eb61.0.3'),('SOP V2','expanded-renewal/sop-v2-1-received.json','expanded-renewal/sop-v2-2-received.json','315c294d-dbc3-4d8f-adc6-e036ad96d1e1.0.3','2b757fa1-ac59-4cbd-aac5-1260f6bcba8a.0.3')]
def metric(a,b):
 i=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)))
 return {'equal':a==b,'old_chars':len(a),'new_chars':len(b),'first_diff_offset':None if a==b else i,'old_at_diff':None if a==b else a[max(0,i-30):i+90],'new_at_diff':None if a==b else b[max(0,i-30):i+90]}
result=[];lines=['# 续班当前实收prompt逐字符裁决','基线91012878；只读已保存LiteLLM实收。当前指本轮最后验证的配置快照，不是本轮重新联网检查。长度为Unicode字符数。完整messages按固定JSON序列化比较（ensure_ascii=False，紧凑分隔符）；不是HTTP原始字节比较。first_diff_offset为0起始。']
for name,af,bf,at,bt in cases:
 a=load(af);b=load(bf)
 if isinstance(b,list):b=b[0]['body']
 am=a['messages'];bm=b['messages'];full=metric(json.dumps(am,ensure_ascii=False,separators=(',',':')),json.dumps(bm,ensure_ascii=False,separators=(',',':')))
 flat=am[0]['content'];sep='  },\n  {\n    "role": "user",\n    "content": "';splits={}
 if name!='SOP V2':
  x,y=flat.split(sep,1);oldsys=x.split('"content": "',1)[1].removesuffix('"\n');olduser=y.removesuffix('"\n  }\n]');pairs=[('system',oldsys,bm[0]['content']),('user',olduser,bm[1]['content'])]
 else:pairs=[('user',am[0]['content'],bm[0]['content'])]
 for role,x,y in pairs:
  splits[role]=metric(x,y);(out/f'current-{name}-{role}.diff').write_text(''.join(difflib.unified_diff(x.splitlines(True),y.splitlines(True),fromfile='old decoded '+role,tofile='new '+role)) or '# identical\n')
 r={'case':name,'old_file':af,'new_file':bf,'old_trace':at,'new_trace':bt,'old_roles':[m['role'] for m in am],'new_roles':[m['role'] for m in bm],'full_messages':full,'decoded_content':splits,'new_parameters':{k:v for k,v in b.items() if k!='messages'}};result.append(r)
 lines+=['\n## '+name,f'旧trace：{at}；新trace：{bt}。',f'旧文件：{af}；新文件：{bf}。',f'实际角色：{r["old_roles"]} → {r["new_roles"]}。','完整messages：'+json.dumps(full,ensure_ascii=False)]
 for role,m in splits.items():lines.append('拆出'+role+'：'+json.dumps(m,ensure_ascii=False))
 lines.append('新请求参数（单列，不混同prompt一致）：'+json.dumps(r['new_parameters'],ensure_ascii=False))
(out/'prompt-current-renewal.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));(out/'prompt-current-renewal.md').write_text('\n\n'.join(lines))
for r in result:print(r['case'],r['full_messages'],r['decoded_content'])
