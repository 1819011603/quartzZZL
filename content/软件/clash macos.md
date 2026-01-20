

clash verge

https://github.com/clash-verge-rev/clash-verge-rev


![[../壁纸/附件/Pasted image 20250517124710.png]]



# Clash Verge Rev v2.4.4 禁用 HTTP/2 设置

```
function main(config) {
  config["tcp-concurrent"] = false;
  config["global-client-fingerprint"] = "chrome";
  config["skip-cert-verify"] = true;
  return config;
}
```

![[../壁纸/附件/Pasted image 20260119144721.png]]

```
/**
 * 配置中的规则"config.rules"是一个数组，通过新旧数组合并来添加
 * @param prependRule 添加的数组
 */
const prependRule = [
  // 将百度分流到直连
  "DOMAIN-SUFFIX,baidu.com,DIRECT",
  "DOMAIN-SUFFIX,github.com,DIRECT",
   "DOMAIN-SUFFIX,baijia.com,DIRECT",
      "DOMAIN-SUFFIX,gaotu.cn,DIRECT",
  "DOMAIN-SUFFIX,feishu.cn,DIRECT",
    "DOMAIN-SUFFIX,trae.ai,DIRECT",

    "DOMAIN-SUFFIX,steamtools.net,DIRECT",
    "DOMAIN-SUFFIX,cursor.sh,自动选择",
  "DOMAIN-SUFFIX,clashverge.dev,自动选择",
];
function main(config) {
  // 把旧规则合并到新规则后面(也可以用其它合并数组的办法)
  let oldrules = config["rules"];
  config["rules"] = prependRule.concat(oldrules);
  config["tcp-concurrent"] = false;
  config["global-client-fingerprint"] = "chrome";
  config["skip-cert-verify"] = true;
  return config;
}
```


已经为部分部门增加了ultra账号，ultra账号额度更高，基本上可以满足使用需求，但是在现阶段也有一些限制。

使用方式如下：

1. 执行工具，选择以baijiahulian邮箱结尾的账号
    
2. 打开你的梯子，选择全局模式或者规则模式，必须设置为系统代理
    
3. 打开cursor里的vs code setting，搜索proxy,禁用http2.0
    

![[../壁纸/附件/img_v3_02u0_b2f1f870-e03e-4f63-a7d4-51903bd504dg.jpg]]

4. 打开cursor里的cursor setting，找到network，选择http1.1
![[../壁纸/附件/img_v3_02u0_f02990e7-9006-428c-9ba7-f58aeaf4410g.jpg]]
