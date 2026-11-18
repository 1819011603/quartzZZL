import json, sys
EXCL={'renewalRole','renewal_role','renewalStartTime','renewalEndTime','imageUrl'}
def norm(x):
    if isinstance(x,dict): return {k:norm(v) for k,v in x.items() if k not in EXCL}
    if isinstance(x,list):
        y=[norm(i) for i in x]; return sorted(y,key=lambda i: json.dumps(i,sort_keys=True,ensure_ascii=False))
    return x
def diff(a,b,p='',out=None):
    out=[] if out is None else out
    if type(a)!=type(b): out.append((p,a,b)); return out
    if isinstance(a,dict):
        for k in sorted(set(a)|set(b)): diff(a.get(k),b.get(k),p+'.'+k,out)
    elif isinstance(a,list):
        if len(a)!=len(b): out.append((p+'[len]',len(a),len(b)))
        for i,(x,y) in enumerate(zip(a,b)): diff(x,y,f'{p}[{i}]',out)
    elif a!=b: out.append((p,a,b))
    return out
pa,pb=sys.argv[1],sys.argv[2]; cases=json.load(open(__import__('os').environ.get('CASES','/tmp/w1func/cases.json'))); res={}
for c in cases:
    i=c['id']
    try: A=json.load(open(f'/tmp/w1func/out/{pa}/{i}.json')); B=json.load(open(f'/tmp/w1func/out/{pb}/{i}.json'))
    except Exception as e: res[i]={'err':str(e)}; print(i,'ERR',e); continue
    d=diff(norm({'status':A.get('status'),'data':A.get('data')}),norm({'status':B.get('status'),'data':B.get('data')}))
    res[i]={'consistent':not d,'ndiff':len(d),'diffs':[[p,str(x)[:120],str(y)[:120]] for p,x,y in d[:15]]}
    print(i,'OK' if not d else f'DIFF {len(d)}', (d[0][0] if d else ''))
json.dump(res,open(f'/tmp/w1func/out/cmp_{pa}_vs_{pb}.json','w'),ensure_ascii=False,indent=1)
