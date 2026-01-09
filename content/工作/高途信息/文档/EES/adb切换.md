
https://docs.baijia.com/aio/DQVhYVmhDcFhCRVRKc3R4TGtC?p=YMSAYaS6S1opDeBSHuN0Kx&nlc=1





### 拦截器

```java
  
import com.baomidou.dynamic.datasource.toolkit.DynamicDataSourceContextHolder;  
import com.baomidou.mybatisplus.core.metadata.TableInfo;  
import com.baomidou.mybatisplus.core.metadata.TableInfoHelper;  
import org.apache.ibatis.cache.CacheKey;  
import org.apache.ibatis.executor.Executor;  
import org.apache.ibatis.executor.statement.StatementHandler;  
import org.apache.ibatis.mapping.BoundSql;  
import org.apache.ibatis.mapping.MappedStatement;  
import org.apache.ibatis.plugin.*;  
import org.apache.ibatis.reflection.MetaObject;  
import org.apache.ibatis.reflection.SystemMetaObject;  
import org.apache.ibatis.session.ResultHandler;  
import org.apache.ibatis.session.RowBounds;  
import org.slf4j.Logger;  
import org.slf4j.LoggerFactory;  
  
import java.sql.Connection;  
import java.util.Properties;  
  
/**  
 * @author: zhangzeling  
 * @date: 2025/3/25  
 * @description: DataSourceSqlInterceptor  
 */  
  
@Intercepts(  
        {  
                @Signature(type = StatementHandler.class, method = "prepare", args = {Connection.class, Integer.class}),  
                @Signature(type = StatementHandler.class, method = "getBoundSql", args = {}),  
                @Signature(type = Executor.class, method = "update", args = {MappedStatement.class, Object.class}),  
                @Signature(type = Executor.class, method = "query", args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class}),  
                @Signature(type = Executor.class, method = "query", args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class, CacheKey.class, BoundSql.class}),  
        }  
)  
public class DataSourceSqlInterceptor implements Interceptor {  
    private static final Logger log = LoggerFactory.getLogger(DataSourceSqlInterceptor.class);  
  
    @Override  
    public Object intercept(Invocation invocation) throws Throwable {  
        if (invocation.getTarget() instanceof StatementHandler) {  
            try {  
                // 获取当前数据源（可结合数据源切换逻辑获取）  
                String currentDataSource = DynamicDataSourceContextHolder.peek();  
                StatementHandler statementHandler = (StatementHandler) invocation.getTarget();  
                // 获取 SQL 语句  
                String sql = statementHandler.getBoundSql().getSql();  
                // 只拦截 ADB_RO_DATA_SOURCE 数据源的 SQL  
                MetaObject metaObject = SystemMetaObject.forObject(statementHandler);  
                MappedStatement mappedStatement = (MappedStatement) metaObject.getValue("delegate.mappedStatement");  
  
                // 获取 MyBatis-Plus 的表信息  
                Class<?> entityClass = mappedStatement.getResultMaps().get(0).getType();  
                TableInfo tableInfo = TableInfoHelper.getTableInfo(entityClass);  
                String tableName = tableInfo != null ? tableInfo.getTableName() : "UNKNOWN";  
                log.info("Intercepted SQL on {}: tableName:{}, sql:{}", currentDataSource, tableName,sql);  
  
            } catch (Exception ignore) {  
            }        }  
  
  
        return invocation.proceed();  
    }  
  
    @Override  
    public Object plugin(Object target) {  
        return Plugin.wrap(target, this);  
    }  
  
    @Override  
    public void setProperties(Properties properties) {}  
}
```


```java
import org.apache.ibatis.plugin.Interceptor;  
import org.springframework.context.annotation.Bean;  
import org.springframework.context.annotation.Configuration;  
  
@Configuration  
public class MybatisPlusConfig {  
    @Bean  
    public Interceptor dataSourceSqlInterceptor() {  
        return new DataSourceSqlInterceptor();  
    }  
}
```




```

CourseCommentCommentMapper                                                                                                                                                              

QuestionnaireMapper                                                                                                                                                                     

SubclazzAnnounceInfoMapper                                                                                                                                                              

UserDefaultMobileMapper                                                                                                                                                                 

CourseCategoryMapper                                                                                                                                                                    

BatchTransferSubclazzTaskMapper                                                                                                                                                         

AlgorithmAutoSelectClazzTaskMapper                                                                                                                                                      

StudentDetailMapper                                                                                                                                                                     

UserLessonLearnMapper                                                                                                                                                                   

UserClazzLearnStatisticMapper                                                                                                                                                           

EmployeeMapper                                                                                                                                                                          

UserLearnDetailMapper                                                                                                                                                                   

CourseExtensionMapper                                                                                                                                                                   

ExpressInvoiceLogisticMapper                                                                                                                                                            

FinishLessonStatisticsMapper                                                                                                                                                            

FinishedClazzMapper                                                                                                                                                                     

ClazzLessonMapper                                                                                                                                                                       

ClazzStudentHomeworkStatisticMapper                                                                                                                                                     

UserSubclazzTagMapper                                                                                                                                                                   

QuestionnaireAnswerMapper                                                                                                                                                               

UserMapper                                                                                                                                                                              

SubclazzExtInfoMapper                                                                                                                                                                   

RefundApplyMapper                                                                                                                                                                       

ClazzLessonSubclazzUserAttendMapper                                                                                                                                                     

CourseMapper                                                                                                                                                                            

LearningStudentInfoExtMapper                                                                                                                                                            

ClazzPeriodMapMapper                                                                                                                                                                    

RightInfoMapper                                                                                                                                                                         

LessonSubclazzLearnStatisticMapper                                                                                                                                                      

SubclazzTeamMapper                                                                                                                                                                      

StudentAssistantInfoRecordMapper                                                                                                                                                        

SubclazzTeamStudentMapper                                                                                                                                                               

MergeSubclazzTaskMapper                                                                                                                                                                 

LearningStudentInfoRecordMapper                                                                                                                                                         

DynamicHistoryDataFailRecordMapper                                                                                                                                                      

QuestionMapper                                                                                                                                                                          

ShouldFinishClazzMapper                                                                                                                                                                 

ClazzMapper                                                                                                                                                                             

SubclazzMapper                                                                                                                                                                          

StudentSituationYubaomingMapper                                                                                                                                                         

TransferSubclazzTaskDetailMapper                                                                                                                                                        

SubclazzStudentExtMapper                                                                                                                                                                

SubclazzStudentMapper                                                                                                                                                                   

TeacherMapper                                                                                                                                                                           

ExpressInvoiceMapper                                                                                                                                                                    

FinishLessonInfoMapper                                                                                                                                                                  

CourseCommentTopicMapper                                                                                                                                                                

MsgSendRecordMapper                                                                                                                                                                     

OrderInfoMapper                                                                                                                                                                         

TransferApplyMapper                                                                                                                                                                     

AutoSelectClazzTaskMapper                                                                                                                                                               

UserDeviceMapper
```




```
SubclazzSpeakStatisticMapper                                                                                                                                                            

LearnUserDragDetailRoMapper                                                                                                                                                             

ClazzLessonLiveDataMapper                                                                                                                                                               

LessonSubclazzLearnStatisticRoMapper                                                                                                                                                    

LearnLessonDetailRoMapper                                                                                                                                                               

ClazzLessonSpeakContentMapper                                                                                                                                                           

UserLessonLearnRoMapper                                                                                                                                                                 

UserClazzLearnStatisticRoMapper                                                                                                                                                         

ClazzLessonRoMapper
```