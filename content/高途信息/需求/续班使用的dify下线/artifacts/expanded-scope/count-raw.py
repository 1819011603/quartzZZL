import pathlib,json,re
p=pathlib.Path(__file__).parent.parent;records={};errors=[]
def walk(o):
 if isinstance(o,dict):
  if o.get('service')=='litellm' and 'Chat_completion request' in o.get('message',''):yield o
  else:
   for v in o.values():yield from walk(v)
 elif isinstance(o,list):
  for v in o:yield from walk(v)
for folder in ['expanded-renewal','expanded-refund','trace-recheck-20261123']:
 for f in (p/folder).iterdir():
  if not ('log' in f.name or f.name in ['dify-thinking-result.json']):continue
  try:
   s=f.read_text();s=s[s.index('\n')+1:] if s.startswith('[窗口') else s;o=json.loads(s)
  except Exception:continue
  for r in walk(o):
   m=r['message'];t=re.search(r'TID:([^\]]+)',m)
   if not t:continue
   try:b=json.loads(m.split(':\n',1)[1])
   except Exception:continue
   key=(t.group(1),m[:23],json.dumps(b,sort_keys=True,ensure_ascii=False));v=records.setdefault(key,{'trace':t.group(1),'time':m[:23],'service':'litellm','model':b.get('model'),'roles':[x['role'] for x in b['messages']],'tools':len(b.get('tools',[])),'sources':[]});v['sources'].append(str(f.relative_to(p)))
a=sorted(records.values(),key=lambda x:(x['trace'],x['time']));(p/'expanded-scope/call-count-raw.json').write_text(json.dumps(a,ensure_ascii=False,indent=2))
for x in a:print(x['trace'],x['time'],x['model'],x['tools'],x['sources'][0])
