> PageHelper的使用

```java
    @Override
    public PageData<WorkPhoneStaffInfo> queryWpStaffList(WpStaffRequest wpStaffRequest) {
        PageHelper.startPage(wpStaffRequest.getPageNum(),wpStaffRequest.getPageSize());
        List<WorkPhoneStaffInfo> workPhoneStaffInfo = physicalAssetPoMapper.selectWxIdByEmailPrefix(wpStaffRequest.getUnameList());
        PageInfo<WorkPhoneStaffInfo> pageInfo = new PageInfo<>(workPhoneStaffInfo);
        int total = (int) pageInfo.getTotal();
        return new PageData<>(workPhoneStaffInfo, wpStaffRequest.getPageNum(), wpStaffRequest.getPageSize(), total);
    }
```



>  PageHelper分页能查出总条数但是列表没有数据

原因：pagehelp分页pagenum从1开始. 因为pagenum不从1开始，pagenum*pageSize> total 所以没有数据


> 为什么PageInfo可以获取total

	PageInfo<WorkPhoneStaffInfo> pageInfo = new PageInfo<>(workPhoneStaffInfo);
	这是因为返回的List<T> 其实是Page类 继承了ArrayList

![[../../壁纸/附件/Pasted image 20240509172427.png]]