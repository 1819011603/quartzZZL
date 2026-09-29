import com.gaotu.clazz.distribution.client.dto.SubclazzStudentDTO;
import com.gaotu.student.data.app.service.syncdata.AdsCourseClazzUserSyncUpdateService;
import com.gaotu.student.data.domain.service.impl.UserLoginTimeService;
import com.gaotu.student.data.infrastructure.acl.SubclazzStudentBizFeignService;
import com.xxl.job.core.biz.model.ReturnT;
import com.xxl.job.core.handler.IJobHandler;
import com.xxl.job.core.handler.annotation.JobHandler;
import com.xxl.job.core.log.XxlJobLogger;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.collections4.MapUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 途途APP活跃时间按班回溯：只重算并写回 tutuAppLastActiveDate / tutuPcLastActiveDate，不走速达全量字段。
 * 取数与实时链路一致（用户中心登录记录 + CDP 最后活跃时间取 max），直接按「班级号-学员ID」写回该班大班花名册文档。
 * executorParam = 班级号，逗号分隔多个。
 */
@Component
@JobHandler(value = "backTutuActiveTimeByClazzHandler")
public class BackTutuActiveTimeByClazzHandler extends IJobHandler {

    private static final List<String> TARGET_FIELDS = Arrays.asList("tutuAppLastActiveDate", "tutuPcLastActiveDate");
    private static final List<Integer> STUDENT_STATUS = Arrays.asList(1, 2, 3);
    private static final int BATCH_SIZE = 100;
    private static final long BATCH_SLEEP_MS = 200L;

    @Resource
    private SubclazzStudentBizFeignService subclazzStudentBizFeignService;

    @Resource
    private UserLoginTimeService userLoginTimeService;

    @Resource
    private AdsCourseClazzUserSyncUpdateService adsCourseClazzUserSyncUpdateService;

    @Override
    public ReturnT<String> execute(String s) throws Exception {
        if (StringUtils.isBlank(s)) {
            XxlJobLogger.log("executorParam 为空，需传班级号（逗号分隔）");
            return ReturnT.FAIL;
        }
        List<Long> clazzNumbers = Arrays.stream(s.split(","))
                .map(String::trim)
                .filter(StringUtils::isNotBlank)
                .map(Long::parseLong)
                .distinct()
                .collect(Collectors.toList());
        XxlJobLogger.log("途途活跃时间按班回溯开始: {} fields:{}", clazzNumbers, TARGET_FIELDS);

        for (Long clazzNumber : clazzNumbers) {
            Set<Long> userIds = new LinkedHashSet<>();
            Long minId = 0L;
            while (true) {
                List<SubclazzStudentDTO> students =
                        subclazzStudentBizFeignService.listByClazzNumberAndMinIdAndStatus(clazzNumber, minId, STUDENT_STATUS);
                if (CollectionUtils.isEmpty(students)) {
                    break;
                }
                minId = students.stream().map(SubclazzStudentDTO::getId).max(Comparator.naturalOrder()).get();
                students.forEach(student -> userIds.add(student.getUserId()));
            }
            int written = 0;
            for (List<Long> batch : partition(new ArrayList<>(userIds), BATCH_SIZE)) {
                written += backBatch(clazzNumber, batch);
                Thread.sleep(BATCH_SLEEP_MS);
            }
            XxlJobLogger.log("班级:{} 学员数:{} 有途途活跃时间并写回:{}", clazzNumber, userIds.size(), written);
        }
        XxlJobLogger.log("途途活跃时间按班回溯完成: {}", clazzNumbers);
        return ReturnT.SUCCESS;
    }

    private int backBatch(Long clazzNumber, List<Long> userIds) {
        Map<Long, Map<String, Long>> loginTime = userLoginTimeService.getUserLoginTime(userIds);
        Map<Long, Map<String, Long>> cdpTime = userLoginTimeService.getCdpActiveTimeMap(userIds);
        Map<Long, Map<String, Long>> merged = userLoginTimeService.mergeActiveTime(userIds, cdpTime, loginTime);

        List<Map<String, Object>> dataList = new ArrayList<>();
        for (Long userId : userIds) {
            Map<String, Long> activeTimeMap = merged.get(userId);
            if (MapUtils.isEmpty(activeTimeMap)) {
                continue;
            }
            Map<String, Object> dataMap = new HashMap<>();
            TARGET_FIELDS.forEach(field -> {
                Long value = activeTimeMap.get(field);
                if (value != null && value > 0L) {
                    dataMap.put(field, value);
                }
            });
            if (dataMap.isEmpty()) {
                continue;
            }
            // 直接按本班文档 ID 写，不走按用户维度发 MQ 的异步链路（有序队列积压时会迟迟不落地）
            dataMap.put("shardingKey", clazzNumber + "-" + userId);
            dataList.add(dataMap);
        }
        if (!dataList.isEmpty()) {
            XxlJobLogger.log("写回明细: {}", dataList);
            adsCourseClazzUserSyncUpdateService.bulkUpsertLargeClazzUser(dataList, 3);
        }
        return dataList.size();
    }

    private static <T> List<List<T>> partition(List<T> list, int size) {
        List<List<T>> result = new ArrayList<>();
        for (int i = 0; i < list.size(); i += size) {
            result.add(list.subList(i, Math.min(i + size, list.size())));
        }
        return result;
    }
}
