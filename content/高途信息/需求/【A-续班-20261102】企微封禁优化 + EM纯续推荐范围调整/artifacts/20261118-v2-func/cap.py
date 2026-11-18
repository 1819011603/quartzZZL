import json, subprocess, sys, os, time
phase=sys.argv[1]; cases=json.load(open(__import__('os').environ.get('CASES','/tmp/w1func/cases.json')))
os.makedirs(f'/tmp/w1func/out/{phase}',exist_ok=True); idx={}
for c in cases:
    url=c['url']; b=f'/tmp/w1func/out/{phase}/{c["id"]}.json'; h=b+'.h'
    subprocess.run(['curl','-s','-H','traffic-env: test-eco-8']+[x for kv in c.get('headers',[]) for x in ('-H',kv)]+['-D',h,'-o',b,'--max-time','120',url])
    tid=''
    for l in open(h,errors='ignore'):
        if l.lower().startswith('gapm-traceid:'): tid=l.split(':',1)[1].strip()
    try:
        d=json.load(open(b)); data=d.get('data') or {}
        n=sum(len(g.get('clazzDetailDTOList') or []) for g in (data.get('gradeClazzList') or []))
        st=d.get('status'); msg=(d.get('msg') or '')[:60]
    except Exception as e: n=None; st='PARSE'; msg=str(e)[:60]
    idx[c['id']]={'tid':tid,'status':st,'items':n,'msg':msg,'ts':time.strftime('%H:%M:%S')}
    print(c['id'],st,n,msg,tid)
json.dump(idx,open(f'/tmp/w1func/out/{phase}/index.json','w'),ensure_ascii=False,indent=1)
