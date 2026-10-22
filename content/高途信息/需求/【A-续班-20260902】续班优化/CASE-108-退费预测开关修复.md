# CASE-108：退费分析卡预测意向跟随开关

## 要解决的问题

关闭退费「意向预测」后，「退费分析」仍显示历史预测等级。原因是分析卡属于 `service_suggestion`，其中的预测行没有单独判断 `prediction`。

## 后端（已实现，7项测试通过，已部署测试环境）

仓库 `student-center`，分支 `feature-xuban-expand-exclude`，提交 `2cc0194a9`。
接口 `POST /roster/refund/analysis`：保留整卡 `service_suggestion` 判断；有分析数据但 `prediction=false` 时，清空 `aiRefundIntent` 和 `aiRefundIntentDesc`。
不删历史数据，不影响手填退费意向、服务建议或 cronus 列表字段。开关缺失/查询失败沿用已有默认开启规则。

## 前端（仅说明，未修改代码）

仓库 `aianalysisinformations`，改两处，照续班已有写法：

1. `src/tabs/refund/index.tsx`：给 hook 传入预测开关。

```tsx
const { userSchema, loading: userSchemaLoading } = useUserSchema(
  params,
  isModuleOn(refundSwitch, REFUND_CODE.INTENT_PREDICTION)
);
```

该文件已导入 `isModuleOn`、`REFUND_CODE`，已有 `refundSwitch`，无需新增依赖。

2. `src/tabs/refund/hooks/useData.tsx`：hook 接收开关，按开关构造行。

```tsx
export function useUserSchema(params: RefundParams, showIntentPrediction = true): {
  loading: boolean;
  userSchema: UserSchemaComponentProps;
} {
  // 保留其余数据获取逻辑
```

把 `summaryItems` 的第一项替换为：

```tsx
...(showIntentPrediction
  ? [{
      label: '预测退费意向',
      value: <RefundIntent intent={state?.aiRefundIntent} desc={state?.aiRefundIntentDesc} />,
      emphasis: true,
    }]
  : []),
```

其余项保持原写法。按开关隐藏整行，不根据接口字段是否为空决定隐藏；开启但无预测数据时仍沿用现有空态。

## 验收

- 服务建议开、预测关：分析卡保留；接口无预测等级/文案；前端「预测退费意向」整行消失。
- 两者开：预测等级和文案正常显示。
- 服务建议关：整张分析卡仍按原规则隐藏。
- 手填意向、服务建议内容不受预测开关影响。
- 已通过7项后端集成测试，覆盖开/关、缺省、空配置、下游503、整卡关闭和无预测数据。
- 流水线1309131已将提交2cc0194a9发布到test-gtbg-dev-1，新pod Eureka UP。真实analysis接口code0，手填意向2/中及服务建议保留；当前样本本来无预测等级，不将此作为关闭场景证明。两tab全部开关读回均true，未调整现场配置。
- AICR当前head任务489状态为取消，不能记为评审通过。
- 尚需前端按上述两处修改后验证页面，不能据后端通过声明整项完成。
