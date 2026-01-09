

1. 忘记设置 "null_value": 0   排序有点问题


#### 第 1 步：更新 Mapping

```
PUT ads_small_clazz_user/_mapping
{
  "properties": {
    "smallRewardCoin": {
      "type": "integer",
      "null_value": 0
    }
  }
}
```

**执行之后的效果：**

- 从现在开始，任何**新索引**的文档，如果 `smallRewardCoin` 的值是 `null`，它将被自动存储为 `0`。
- 任何被**更新**的文档，如果更新操作中将 `smallRewardCoin` 设置为 `null`，它也会被存储为 `0`。
- 已经存在于索引中的旧文档**保持原样**，它们仍然没有 `smallRewardCoin` 这个字段


#### 第 2 步：修复已经存在的旧数据（推荐）

你的索引中现在存在数据不一致的情况：旧文档没有这个字段，而新文档会因为 `null_value` 的作用而拥有一个默认值。为了让所有数据保持一致，你需要修复旧数据。

最简单的方法是使用 `_update_by_query` API。这个 API 可以查询出所有符合条件的文档，并对它们执行一个更新脚本。

**我们的目标**：找到所有**不存在** `smallRewardCoin` 字段的文档，并给它们加上 `smallRewardCoin: 0`。

```

POST ads_small_clazz_user/_update_by_query
{
  "query": {
    "bool": {
      "must_not": [
        {
          "exists": {
            "field": "smallRewardCoin"
          }
        }
      ]
    }
  },
  "script": {
    "source": "ctx._source.smallRewardCoin = 0",
    "lang": "painless"
  }
}
```

