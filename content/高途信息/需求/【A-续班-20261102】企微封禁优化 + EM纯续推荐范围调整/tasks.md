# 任务板

## 待办

- [ ] T-1 product-server：`/b/renewMaster/list` 支持 number 批量精确搜索
- [ ] T-2 cart：推荐并集（仅纯续，主+从）+ 预热适配
- [ ] T-3 order：跨授课模式受控放行（默认 false）
- [ ] T-4 GAIA：为 `continuationService`/`microContinuationService` 创建 `studentTagNames` 显示记录（需管理员）
- [ ] T-5 student-center：放开两套续班字段配置
- [ ] T-6 编译 → 部署 `test-gtbg-dev-3` → pod UP → 接口验证

## 已完成

- [x] 4 仓分支（origin/release，--no-track）
- [x] test 建表 `gaotu.renew_master_relation`
- [x] cart Apollo 开关已发布=false
- [x] product-server 关系持久层/服务/控制器 + DTO 下发填充；接口收敛为单个 relation/save；编译通过，push `e16e3a27`
- [x] 文档表结构与接口协议章节
