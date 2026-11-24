#!/usr/bin/env python3
"""Prepare only by default. Explicit run after deployment; parse offline actual TEST SLS logs."""
import argparse,json,pathlib,subprocess,re,difflib
BASE=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('mode',choices=['list','run','extract']);p.add_argument('--case');p.add_argument('--commit');p.add_argument('--run',type=pathlib.Path);p.add_argument('--log',type=pathlib.Path);a=p.parse_args()
plan=json.loads((BASE/'format-validation-plan.json').read_text())
if a.mode=='list':
 for c in plan['cases']:print(c['name'],c['status'])
 raise SystemExit()
c=next(c for c in plan['cases'] if c['name']==a.case)
if a.mode=='run':
 if c['status']!='ready' or not a.commit:p.error('requires ready case and verified deployed --commit; never force skipped cases')
 out=BASE/'format-runs'/a.commit/c['name'];out.mkdir(parents=True,exist_ok=True)
 if (out/'response.json').exists():p.error('response already exists: inspect before rerun')
 body=json.loads((BASE/c['request']).read_text())
 assert body['params'][2]=='test'
 assert plan['endpoint'].startswith('https://test-fuwu.baijia.com/')
 assert body['serviceNameAndMethodName'].endswith('#quickTestAiApplication'),'only gateway quickTest allowed'
 assert c.get('mode','quick') in ('quick','quick_reconstructed')
 if c['name']=='退费根因':assert body['params'][0]=='退费根因分析'
 (out/'request.json').write_text(json.dumps(body,ensure_ascii=False,indent=2))
 r=subprocess.run(['curl','-sk','--max-time','180','-x','http://127.0.0.1:8888','-D',str(out/'headers.txt'),plan['endpoint'],'-H','content-type: application/json','-H','traffic-env: test-gtbg-dev-1','-H','identification: microLessonStudent','--data-binary',json.dumps(body,ensure_ascii=False)],capture_output=True,text=True)
 (out/'response.json').write_text(r.stdout);trace=re.search(r'(?im)^gapm-traceid:\s*(\S+)',(out/'headers.txt').read_text());tid=trace.group(1) if trace else None
 (out/'run.json').write_text(json.dumps({'commit':a.commit,'case':c['name'],'mode':c.get('mode','quick'),'trace':tid,'curl_exit':r.returncode,'request_source':c['request']},ensure_ascii=False,indent=2))
 j=json.loads(r.stdout);assert r.returncode==0 and j.get('code')==0,j.get('msg');d=next(iter(j['data'].values()))
 sides=[d]
 assert all(isinstance(x,dict) and x.get('event')!='ERROR' and x.get('answer') for x in sides),'missing successful side'
 assert tid,'missing trace'
 print('trace:',tid,'event:',d.get('event'))
 query={'queryStr':'"'+tid+'"','env':'test','backend':'sls','logType':'app','limit':100}
 print('Query via mcpcli qingzhou_observe get_log_v2 with JSON:',json.dumps(query));print('Save FULL returned log artifact, not mcpcli truncation preview, then extract --log FILE. Include request and Response received by LiteLLM. Historical old baseline only; never trigger old-side inference or PROD.')
else:
 if not a.log or not a.run:p.error('--log and --run run.json required')
 run=json.loads(a.run.read_text());tid=run['trace']
 assert tid and run.get('case')==c['name'],'run case/trace missing or mismatched'
 def extract(path):
  text=path.read_text();start=text.find('[{');assert start>=0,'full JSON rows required'
  rows,_=json.JSONDecoder().raw_decode(text[start:]);assert len(rows)<100,'possible truncation'
  requests=[];responses=[]
  for row in rows:
   m=row.get('message','')
   if row.get('service')!='litellm':continue
   if 'Chat_completion request' not in m and 'Response received by LiteLLM:' not in m:continue
   match=re.search(r'\[TID:([^\]]+)\]',m)
   assert match and match.group(1)==tid,'log trace mismatches run.json'
   if 'Chat_completion request' in m:
    requests.append(json.loads(m.split('\n',1)[1]))
   else:responses.append(json.loads(m.split('Response received by LiteLLM:',1)[1].strip()))
  assert len(requests)==1 and len(responses)==1,'need exactly one full request AND response; inspect rounds/missing logs'
  path.with_suffix('.received.json').write_text(json.dumps({'trace':tid,'request':requests[0],'response':responses[0]},ensure_ascii=False,indent=2))
  return requests[0]['messages']
 actual=extract(a.log)
 old=json.loads((BASE/c['old_messages']).read_text())
 dest=a.log.with_suffix('.messages.json');dest.write_text(json.dumps(actual,ensure_ascii=False,indent=2))
 diff='\n'.join(difflib.unified_diff(json.dumps(old,ensure_ascii=False,indent=2).splitlines(),json.dumps(actual,ensure_ascii=False,indent=2).splitlines(),fromfile='old actual',tofile=str(dest)))
 a.log.with_suffix('.messages.diff').write_text(diff);print('exact_messages_equal',old==actual);print('warnings',c['warnings']);print('actual',dest)
