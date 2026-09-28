# 课节学员 / 课后督学（EM）（lessonStudentList · bs=emLessonAfterUser）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonStudentList?ln=<课节号>&scn=<辅导班号>&cn=<班级号>&bs=emLessonAfterUser` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lessonStudent/index.js` |
| tab 组件 | `src/pages/lessonStudent/EmLessonAfter/`（`./EmLessonAfter`） |
| 主 service 文件 | `src/services/emLessonAfterUser.js` |
| 后端主服务 | **content-analysis**（网关前缀 `intranet-rpc/tutu/content/analysis`） |

> 页面级接口（gray / scene count / 课节 / updateList / 自定义列）见 [_page.md](./_page.md)。仅大班课（`lessonType=normal`）展示。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页/排序 | `getEmLessonAfterUserPageList` | `/intranet-rpc/tutu/content/analysis/lesson/after/user/page` | `src/services/emLessonAfterUser.js:4`（调用 `src/pages/lessonStudent/EmLessonAfter/index.js:219`） | content-analysis | `/tutu/content/analysis/lesson/after/user/page` | 分页查询课后督学学员详情，随分页数据返回同源的P等级指标 [5248783] | **主列表数据**（含 `stat` P 等级指标） |
| 进页面/切换课节/刷新 | `getLessonAfterConfig` | `/intranet-rpc/tutu/content/analysis/lesson/after/config` | `src/services/emLessonAfterUser.js:11`（调用 `.../EmLessonAfter/index.js:144`） | content-analysis | `/tutu/content/analysis/lesson/after/config` | 查询课后督学通用配置 [5248784] | 课节反馈入口/P 等级选项/客户端配置 |
| 课节数据卡片 | `getEmLessonAfterUserStatistic` | `/component/student-center/lesson/after/statistic` | `src/services/emLessonAfterUser.js:17`（调用 `.../EmLessonAfter/components/DataStaticToolCard/index.js:143`） | student-center | `/lesson/after/statistic` | [POST]/statistic [1159250] | 有效听课率/练习提交率/练习订正率 |

## 青舟接口详情页

- [POST /tutu/content/analysis/lesson/after/user/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5248783&appId=content-analysis&branchName=release)
- [POST /tutu/content/analysis/lesson/after/config](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5248784&appId=content-analysis&branchName=release)
- [POST /lesson/after/statistic](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159250&appId=student-center&branchName=release)
