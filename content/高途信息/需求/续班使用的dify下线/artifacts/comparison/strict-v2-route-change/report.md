# TEST旧别名路由配置结果

标准管理能力已执行，但三个旧别名均被save拒绝：模型不存在或已下线。不是新增成功，也未触发生成。

回读gps-ai/test仍14条，逐对象与before完全一致；无新建ID，无需回退。配置入口 https://tech.baijia.com/ai-service/access/gps-ai/route；保存接口 POST https://ai.baijia.com/llm-gateway/admin/callerRoute/save。

最小外部缺口：平台需提供支持redirect源模型的TEST caller路由授权入口，或修正该保存校验。不能改生产、启用已下线模型、改admin或借用他人caller绕过。本任务未采取这些操作。
