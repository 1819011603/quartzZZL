import json, os
PA=os.environ.get('PA','off'); PB=os.environ.get('PB','on')
EX={'renewalRole','renewal_role'}
def items(d):
    out={}
    for g in (d.get('data') or {}).get('gradeClazzList') or []:
        for i in g.get('clazzDetailDTOList') or []:
            k=(g.get('grade'),i.get('productType'),i.get('productSkuNumber'),i.get('beforeCourseNumber'),i.get('afterCourseNumber'))
            out[k]={x:y for x,y in i.items() if x not in EX}
    return out
def grades(d): return {g.get('grade'):(g.get('gradeName'),g.get('defaultSelect')) for g in (d.get('data') or {}).get('gradeClazzList') or []}
cases=json.load(open(__import__('os').environ.get('CASES','cases.json'))); res={}
for c in cases:
    i=c['id']; A=json.load(open(f'out/{PA}/{i}.json')); B=json.load(open(f'out/{PB}/{i}.json'))
    ia,ib=items(A),items(B)
    missing=[k for k in ia if k not in ib]
    changed=[(k,[f for f in set(ia[k])|set(ib[k]) if ia[k].get(f)!=ib[k].get(f)]) for k in ia if k in ib and ia[k]!=ib[k]]
    added=[k for k in ib if k not in ia]
    top={f:(A.get('data',{}) or {}).get(f) for f in ('allSignUp','renewalForceBuy')}; topb={f:(B.get('data',{}) or {}).get(f) for f in ('allSignUp','renewalForceBuy')}
    ga,gb=grades(A),grades(B)
    gchg={g:(ga[g],gb.get(g)) for g in ga if ga[g]!=gb.get(g)}
    res[i]=dict(old=len(ia),v2=len(ib),missing=[list(map(str,k)) for k in missing],changed=[[list(map(str,k)),f] for k,f in changed],added=[list(map(str,k)) for k in added],top_old=top,top_v2=topb,grade_changed={str(k):v for k,v in gchg.items()})
    flag='SUPERSET' if not missing and not changed else 'REGRESS?'
    print(i,flag,f"old={len(ia)} v2={len(ib)} miss={len(missing)} chg={len(changed)} add={len(added)}", ('top' if top!=topb else ''), ('grade' if gchg else ''))
json.dump(res,open(f'out/superset_{PA}.json','w'),ensure_ascii=False,indent=1)
