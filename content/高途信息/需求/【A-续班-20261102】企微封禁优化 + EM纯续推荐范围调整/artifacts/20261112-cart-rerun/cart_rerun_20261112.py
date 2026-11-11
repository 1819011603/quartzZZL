import sys,json,time,pathlib,requests,concurrent.futures
sys.path.insert(0,'/Users/gaotu/.local/mcp-servers')
import baijia_invoke as b
out=pathlib.Path('/Users/gaotu/githubDir/quartzZZL/content/高途信息/需求/【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整/artifacts/20261112-cart-rerun')
lane=sys.argv[1] if len(sys.argv)>1 else 'test-eco-1'; ip={'test-eco-1':'10.218.249.187','test-gtbg-dev-1':'10.218.249.114','test-eco-7':'10.218.237.35'}[lane];out=out/lane;out.mkdir(exist_ok=True);base=f'http://{ip}:28688';headers={'traffic-env':lane,'Host':'CART.GAOTU100.COM'}
def flatten(data):
 if not isinstance(data,dict):return []
 return [dict(grade=g.get('grade'),**{k:d.get(k) for k in ['productSkuNumber','productType','recommendType','beforeCourseNumber','signUp','price','forceBuy']}) for g in data.get('gradeClazzList',[]) for d in g.get('clazzDetailDTOList',[])]
def query(case,plan,user,mode,stage='before'):
 path=(f'/web/renewal/cart?renewalNumber={plan}&appointUserId={user}&includeBCart=false' if mode=='C' else f'/web/renewal/operation/cart?renewalNumber={plan}&userId={user}&fromC={1 if mode=="BC" else 0}')
 start=time.monotonic();r=requests.get(base+path,headers=headers,timeout=55);data=r.json()
 raw={'path':path,'instance':ip,'lane':lane,'duration_ms':round((time.monotonic()-start)*1000),'http':r.status_code,'trace':r.headers.get('GAPM-TraceID'),'response':data}
 name=f'{case}-{mode}-{stage}';(out/(name+'.json')).write_text(json.dumps(raw,ensure_ascii=False,indent=2))
 result={'case':case,'mode':mode,'stage':stage,'code':data.get('code'),'trace':raw['trace'],'ms':raw['duration_ms'],'allSignUp':(data.get('data') or {}).get('allSignUp'),'items':flatten(data.get('data'))}
 print(json.dumps(result,ensure_ascii=False),flush=True);return result
if __name__=='__main__':
 samples=[('M','588858850300473344','7658129872'),('A','585960797778243584','7658129872'),('B','586116340522184704','7658129872'),('J','545361759016388608','654745'),('JS','551533000353986560','654745'),('M2','588858850300473344','7707220467')]
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
  fs=[ex.submit(query,*sample,mode) for sample in samples for mode in ['C','B','BC']]
  for f in fs:
   try:results.append(f.result())
   except Exception as e: print('ERROR',type(e).__name__,str(e)[:200],flush=True)
 (out/'before-summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
