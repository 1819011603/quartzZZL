import sys,json,pathlib
sys.path.insert(0,'/Users/gaotu/.local/mcp-servers');import baijia_invoke as b
p=pathlib.Path('/tmp/renewal-cache-followup');main='588858850300473344';subs=['585960797778243584','586116340522184704']
def invoke(name,method,params):
 r=b.invoke_service('cart',method,params,'test-gtbg-dev-3',None,None);(p/(name+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2));assert not r.get('errors'),r.get('errors');print(name,r.get('traceId'),flush=True);return r['result']
def save(name,values):
 r=b.invoke_http(project='product-server',path='/product-b/b/renewMaster/relation/save',body={'mainRenewMasterNumber':main,'subRenewMasterNumbers':values},traffic_env='test-gtbg-dev-3',b_client='EES');(p/(name+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2));assert r.get('response',{}).get('code')==0,r;print(name,r.get('traceId'),flush=True)
c=invoke('before-plan','com.gaotu.renewal.RenewalDataService#listRenewalMasterByRenewalNumber',[main]);assert set(map(str,c['related_renew_master_numbers']))==set(subs)
# Bind DTO with Java property names, as the reflection bridge uses Gson rather than response snake_case.
def dto(config):
 return {'renewalNumber':main,'courseNumbers':config['course_numbers'],'productType':config['productType'],'type':config['type'],'relatedRenewMasterNumbers':config.get('related_renew_master_numbers',[]),'beginTime':config['beginTime'],'endTime':config['endTime']}
invoke('before-cache-hit','com.gaotu.renewal.RenewalService#corePreheatCache',[dto(c),'7707220467'])
try:
 save('before-clear',[])
 cleared=invoke('before-cleared-plan','com.gaotu.renewal.RenewalDataService#listRenewalMasterByRenewalNumber',[main]);assert not cleared.get('related_renew_master_numbers')
 invoke('before-cleared-cache','com.gaotu.renewal.RenewalService#corePreheatCache',[dto(cleared),'7707220467'])
 invoke('before-cleared-b','com.gaotu.renewal.RenewalService#getRenewalDetail',['7707220467',main,True,True,None])
finally:
 save('before-restore',subs)
 invoke('before-restored-plan','com.gaotu.renewal.RenewalDataService#listRenewalMasterByRenewalNumber',[main])
