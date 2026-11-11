import sys,json,time,concurrent.futures
sys.argv=[sys.argv[0],'test-eco-1']
from cart_rerun_20261112 import *
samples=[('M','588858850300473344','7658129872'),('A','585960797778243584','7658129872'),('B','586116340522184704','7658129872'),('J','545361759016388608','654745'),('JS','551533000353986560','654745'),('M2','588858850300473344','7707220467')]
results=[]
for case,plan,user in samples:
 path=f'/web/renewal/preheat?renewalNumber={plan}&userId={user}'
 start=time.monotonic();r=requests.get(base+path,headers=headers,timeout=55)
 try: data=r.json()
 except ValueError:data=r.text
 raw={'path':path,'instance':ip,'lane':lane,'duration_ms':round((time.monotonic()-start)*1000),'http':r.status_code,'trace':r.headers.get('GAPM-TraceID'),'response':data}
 (out/(case+'-preheat.json')).write_text(json.dumps(raw,ensure_ascii=False,indent=2))
 print('PREHEAT',case,raw['http'],raw['duration_ms'],json.dumps(data,ensure_ascii=False)[:200],flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
  results.extend(ex.map(lambda mode:query(case,plan,user,mode,'after'),['C','B','BC']))
(out/'after-summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
