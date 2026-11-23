import json,pathlib,re,difflib,hashlib
p=pathlib.Path(__file__).parent
cases=[('旅程','prod-tid-cc31e065-full.log','llm-full-c9335c5b.log'),('课程体验','prod-all-e02.log','llm-full-c2512c21.log'),('NPS','prod-all-d200.log','llm-full-fa98c35e.log'),('降退费','prod-trace-service-main.log','llm-full-419e58d2.log'),('素养建议','prod-all-5e25.log','llm-full-7dbd83e7.log')]
summary=[];lines=['# 五场景原始日志精确复核','只读2026-11-23既有日志；部署91012878。按service=litellm且Chat_completion request筛选，以完整TID配对，不用messageId代替trace。轮次数仅针对已保存日志，不外推不可见调用。']
for name,oldfile,newfile in cases:
 entry={'case':name,'sides':{}}
 for side,file in [('prod',oldfile),('test',newfile)]:
  s=(p/file).read_text();rows=json.loads(s[s.index('\n')+1:]);found=[]
  for row in rows:
   m=row.get('message','')
   if row.get('service')!='litellm' or 'Chat_completion request' not in m:continue
   body=json.loads(m.split(':\n',1)[1]);n=len(found)+1;stem=f'exact-{name}-{side}-{n}';(p/(stem+'.json')).write_text(json.dumps(body,ensure_ascii=False,indent=2));found.append({'tid':re.search(r'TID:([^\]]+)',m).group(1),'time':m[:23],'service':row['service'],'source':file,'body_file':stem+'.json','body':body})
  entry['sides'][side]=found
 old=entry['sides']['prod'][0]['body'];new=entry['sides']['test'][0]['body'];assert len({x['tid'] for v in entry['sides'].values() for x in v})==1
 lines+=['\n## '+name,'|环境/轮次|完整TID|时间|service|角色|tools|','|---|---|---|---|---|---|']
 for side,items in entry['sides'].items():
  for i,x in enumerate(items,1):lines.append(f"|{side}/{i}|{x['tid']}|{x['time']}|litellm|{','.join(m['role'] for m in x['body']['messages'])}|{len(x['body'].get('tools',[]))}|")
 lines+=['\n|参数（首轮）|PROD|TEST|','|---|---|---|']
 for k in sorted(set(old)|set(new)):
  if k not in ['messages','tools']:lines.append('|'+k+'|'+json.dumps(old.get(k,'<未传>'),ensure_ascii=False)+'|'+json.dumps(new.get(k,'<未传>'),ensure_ascii=False)+'|')
 oldmessages=old['messages'];flat=next((m['content'] for m in oldmessages if m['role']=='user'),'');sep='  },\n  {\n    "role": "user",\n    "content": "';normalized={}
 if sep in flat:
  a,b=flat.split(sep,1);normalized={'system':'\n'.join(m['content'] for m in oldmessages if m['role']=='system')+'\n'+a.split('"content": "',1)[1].removesuffix('"\n'),'user':b.removesuffix('"\n  }\n]')}
 else:normalized={r:'\n'.join(m.get('content','') or '' for m in oldmessages if m['role']==r) for r in ['system','user']}
 entry['comparison']={}
 for role in ['system','user']:
  a=normalized[role];b='\n'.join(m.get('content','') or '' for m in new['messages'] if m['role']==role);fn=f'exact-{name}-{role}.diff';(p/fn).write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='old normalized '+role,tofile='new actual '+role)) or '# identical\n');entry['comparison'][role]={'equal':a==b,'old_chars':len(a),'new_chars':len(b),'diff':fn};lines.append(f'\n{role}: 相等={a==b}，旧/新字符数={len(a)}/{len(b)}；见{fn}。')
 lines.append('提示词完整body按轮保存为exact-场景-环境-轮次.json；原始messages不做角色合并，diff仅额外提供旧flat展开后的对照。')
 summary.append(entry)
(p/'summary-exact.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(p/'report-exact.md').write_text('\n'.join(lines))
for x in summary: print(x['case'],x['comparison'])
