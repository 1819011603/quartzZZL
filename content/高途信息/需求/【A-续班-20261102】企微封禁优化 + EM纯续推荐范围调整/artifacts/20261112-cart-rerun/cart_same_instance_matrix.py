import pathlib,subprocess
out=pathlib.Path('/Users/gaotu/githubDir/quartzZZL/content/高途信息/需求/【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整/artifacts/20261112-cart-rerun/test-eco-1')
samples=[('A',7658129872,585960797778243584),('M2',7707220467,588858850300473344),('J',654745,545361759016388608)]
items=[]
for case,user,plan in samples:
 for skip in ['false','true']:
  project="#{'allSignUp':#v.allSignUp,'grades':#v.gradeClazzList.{#{'grade':#this.grade,'defaultSelect':#this.defaultSelect,'items':#this.clazzDetailDTOList.{#{'sku':#this.productSkuNumber,'signUp':#this.signUp,'price':#this.price,'name':#this.productSkuName,'forceBuy':#this.forceBuy,'type':#this.recommendType}}}}}"
  items.append("'"+case+'-skip-'+skip+"':(#v=instances[0].getRenewalDetail("+f'{user}L,{plan}L,false,false,{user}L,null,false,{skip}'+'),'+project+')')
exp='#{'+','.join(items)+'}.toString()'
cmd=['python3','/Users/gaotu/.claude/skills/pod-terminal/pod_term.py','arthas','--service-code','gaotu_cart','--env','dev','--pod-name','cart-gaotu100-com-cd4cb7b69-qnmwr','--command',f'vmtool -x 2 --action getInstances --className com.gaotu.renewal.RenewalService --express "{exp}"','--stop']
r=subprocess.run(cmd,capture_output=True,text=True,timeout=100)
(out/'same-instance-cache-vs-realtime.txt').write_text(r.stdout+'\n'+r.stderr);print(r.returncode);print(r.stdout);print(r.stderr)
