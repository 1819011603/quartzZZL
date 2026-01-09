
```
[{"fieldNumber":10001},{"fieldNumber":10020},{"fieldNumber":10007},{"fieldNumber":10015},{"fieldNumber":10019},{"fieldNumber":10013},{"fieldNumber":10016},{"fieldNumber":70010},{"fieldNumber":70007},{"fieldNumber":80006},{"fieldNumber":30009},{"fieldNumber":80001},{"fieldNumber":70011},{"fieldNumber":80005},{"fieldNumber":70009},{"fieldNumber":80002},{"fieldNumber":80003},{"fieldNumber":10014},{"fieldNumber":70066},{"fieldNumber":80004},{"fieldNumber":70068},{"fieldNumber":10009},{"fieldNumber":70069},{"fieldNumber":70001},{"fieldNumber":70070},{"fieldNumber":70014},{"fieldNumber":70071},{"fieldNumber":90001},{"fieldNumber":70042},{"fieldNumber":10008},{"fieldNumber":30011},{"fieldNumber":60005},{"fieldNumber":60006},{"fieldNumber":10010},{"fieldNumber":60007},{"fieldNumber":70016},{"fieldNumber":10011},{"fieldNumber":10012},{"fieldNumber":70008},{"fieldNumber":70013},{"fieldNumber":70005},{"fieldNumber":90002},{"fieldNumber":90003},{"fieldNumber":90004},{"fieldNumber":90005},{"fieldNumber":90008}]
```


json 字段提取
```

pbpaste | jq '.[].key' | pbcopy

pbpaste | jq '.[].[com.gaotu.reach.adapter.business.staff.StaffAdapter#listByOrgNumbers].[].orgNamePath' | pbcopy

pbpaste | jq '.hits.hits.[]._id' | pbcopy
```



- **升序排序**：`jq 'sort_by(.number)'`
- **降序排序**：`jq 'sort_by(.number) | reverse'`

pbpaste | jq 'sort_by(.number)' | pbcopy


```

pbpaste | jq '
  sort_by(.clazzNumber)
  | map(
      .smallStudyingSubjectList |=
        sort_by(
          (.smallStudyingSubjectId | tonumber),
          .courseDepartmentNumber
        )
    )
' | pbcopy
```