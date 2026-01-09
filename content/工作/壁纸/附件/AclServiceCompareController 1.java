package com.gaotu.yunying.student.center.web.api;

import com.alibaba.fastjson.JSON;
import com.gaotu.arch.vomodel.model.RVO;
import com.google.gson.Gson;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.springframework.aop.framework.Advised;
import org.springframework.aop.support.AopUtils;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.core.ResolvableType;
import org.springframework.core.convert.ConversionService;
import org.springframework.core.convert.support.DefaultConversionService;
import org.springframework.util.ClassUtils;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.lang.reflect.*;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * ACL服务对比测试Controller
 * 提供通过POST方法，动态查找和调用不同实现类的方法进行结果对比
 *
 * @author system
 * @date 2024/12/17
 */
@RestController
@RequestMapping("/test/acl/compare")
@Api(tags = "ACL服务对比测试接口")
@Slf4j
public class AclServiceCompareController implements ApplicationContextAware {

    private final static Gson gson = new Gson();
    private final ConversionService conversionService = DefaultConversionService.getSharedInstance();
    private ApplicationContext applicationContext;
    @Value("${AclServiceCompareController.enabled:true}")
    private boolean enabled;

    public static String getParentParentPackage(Class<?> clazz) {
        String className = clazz.getName();
        int lastDotIndex = className.lastIndexOf('.');

        if (lastDotIndex == -1) {
            return null; // 没有包路径
        }

        String packageName = className.substring(0, lastDotIndex);
        int secondLastDotIndex = packageName.lastIndexOf('.');

        if (secondLastDotIndex == -1) {
            return null; // 包路径不足两级
        }

        int thirdLastDotIndex = packageName.substring(0, secondLastDotIndex).lastIndexOf('.');

        if (thirdLastDotIndex == -1) {
            return packageName.substring(0, secondLastDotIndex);
        } else {
            return packageName.substring(0, thirdLastDotIndex);
        }
    }

    public static Type[] extractAndPrintListElementType(Method method, int paramIndex) {
        Type[] genericParameterTypes = method.getGenericParameterTypes();

        if (paramIndex >= genericParameterTypes.length) {
            return null;
        }
        Type paramType = genericParameterTypes[paramIndex];


        // 判断是否为 ParameterizedType (即带有泛型参数的类型，如 List<Long>)
        if (paramType instanceof ParameterizedType) {
            ParameterizedType pType = (ParameterizedType) paramType;

            // 获取原始类型 (例如 List.class)
            Type rawType = pType.getRawType();
            Type[] actualTypeArguments = pType.getActualTypeArguments();
            log.info("方法 {} 的第 {} 个参数类型: {}, 原始类型: {}, 泛型参数: {}",
                    method.getName(), paramIndex, paramType.getTypeName(),
                    rawType.getTypeName(), Arrays.toString(actualTypeArguments));
            return actualTypeArguments;
        }

        return null;
    }

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        this.applicationContext = applicationContext;
    }

    /**
     * 通过POST方法对比服务的不同实现
     *
     * @param request 包含服务名称、方法名和参数的请求
     * @return 不同实现的结果对比
     */
    @PostMapping("/service")
    @ApiOperation(value = "对比服务的不同实现结果", notes = "通过服务名称动态查找实现并调用方法")
    public RVO<Map<String, Object>> compareService(@RequestBody ServiceCompareRequest request) {
        return getMapRVO(request);
    }

    @PostMapping("/services")
    @ApiOperation(value = "对比服务的不同实现结果", notes = "通过服务名称动态查找实现并调用方法")
    public RVO<List<Map<String, Object>>> compareServices(@RequestBody List<ServiceCompareRequest> requests) {
        List<RVO<Map<String, Object>>> collect = requests.stream().map(this::getMapRVO).collect(Collectors.toList());
        RVO<List<Map<String, Object>>> data = RVO.data(collect.stream().map(RVO::getData).collect(Collectors.toList()));
        collect.stream().filter(rvo -> rvo.getCode() != 0).findFirst().ifPresent(rvo -> {
            data.setMsg(rvo.getMsg());
        });
        return data;
    }

    private @NotNull RVO<Map<String, Object>> getMapRVO(ServiceCompareRequest request) {
        if (!enabled) {
            return RVO.fail(1, "ACL服务对比功能未启用");
        }
        try {
            // 1. 查找服务实现类
            String[] strings = request.getServiceNameAndMethodName().split("#");

            if (strings.length != 2) {
                return RVO.fail(1, "serviceNameAndMethodName 格式错误，应为 '完整类名#方法名'");
            }

            String serviceName = strings[0];
            String methodName = strings[1];
            Map<String, Object> implementationsMap = findServiceImplementations(serviceName, methodName);
            if (implementationsMap.isEmpty()) {
                return RVO.fail(1, "未找到服务 " + serviceName + " 的实现类");
            }

            // 2. 解析参数
            List<Object> methodParams = request.getParams();

            // 3. 调用方法并收集结果
            Map<String, Object> result = new HashMap<>();
            for (Map.Entry<String, Object> entry : implementationsMap.entrySet()) {
                String implName = entry.getKey();
                Object implInstance = entry.getValue();

                try {
                    // 查找匹配的方法
                    Method method = findMethod(implInstance, implInstance.getClass(), methodName, methodParams, result, implName);
                    if (method == null) {
                        log.warn("在实现类 {} 中未找到方法 {}", implName, methodName);
                        result.put(implName + "_error", "未找到方法 " + methodName);
                        continue;
                    }


                } catch (Exception e) {
                    log.warn("调用 {} 的 {} 方法时出错", implName, methodName, e);
                    result.put(implName + "_error", e.toString());
                }
            }

            if (result.isEmpty()) {
                return RVO.fail(1, "未能成功调用任何实现类的 " + methodName + " 方法");
            }

            return RVO.data(result);

        } catch (Exception e) {
            log.warn("对比服务实现时出错", e);
            return RVO.fail(1, "对比服务实现时出错: " + e.getMessage());
        }
    }

    /**
     * 查找服务的所有实现类
     */
    private Map<String, Object> findServiceImplementations(String serviceName, String methodName) {
        Map<String, Object> result = new HashMap<>();

        try {
            Class<?> aClass = Class.forName(serviceName, false, Thread.currentThread().getContextClassLoader());
            Map<String, ?> beansOfType = applicationContext.getBeansOfType(aClass);
            if (aClass.isInterface() || beansOfType.size() > 1) {
                if (beansOfType.isEmpty()) {
                    log.warn("未找到服务接口 {} 的实现类", serviceName);
                    return result;
                }
                return beansOfType.entrySet().stream()
                        .filter(entry -> hasMethod(entry.getValue().getClass(), methodName))
                        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));


            }
            Object serviceImpl = getBean(serviceName);
            if (serviceImpl != null) {
                String prePath = getParentParentPackage(serviceImpl.getClass());
                result.put(serviceName, serviceImpl);
                String implName;
                try {
                    implName = serviceName.substring(0, serviceName.lastIndexOf("Impl"));
                } catch (Exception e) {
                    return result;
                }
                // 2. 尝试查找V1实现
                String v1ImplName = implName + "V1Impl";
                Object serviceV1Impl = getBean(v1ImplName);
                if (serviceV1Impl != null) {
                    result.put(v1ImplName, serviceV1Impl);
                }

                // 3. 如果找不到V1实现，查找原始实现类的所有父接口的实现类
                if (serviceV1Impl == null) {
                    // 获取原始实现类的所有接口
                    Class<?>[] interfaces = serviceImpl.getClass().getInterfaces();
                    for (Class<?> interfaceClass : interfaces) {
                        // 排除一些常见的Spring接口
                        if (interfaceClass.getName().startsWith("org.springframework") ||
                                interfaceClass.getName().startsWith("java.")
                                || !interfaceClass.getName().startsWith(prePath)) {
                            log.debug("跳过接口 {}", interfaceClass.getName());
                            continue;
                        }

                        log.info("查找接口 {} 的所有实现类", interfaceClass.getName());

                        // 获取该接口的所有实现类
                        beansOfType.values().forEach(
                                bean -> {
                                    if (!result.containsKey(bean.getClass().getName())) {
                                        if (hasMethod(bean.getClass(), methodName)) {
                                            result.put(bean.getClass().getName(), bean);
                                            log.info("找到接口 {} 的实现类: {}", interfaceClass.getName(), bean);
                                        }
                                    }

                                }
                        );
                    }
                }
            } else {
                log.warn("未找到服务实现类: {}", serviceName);
            }

        } catch (Exception e) {
            log.warn("查找服务实现时出错", e);
        }

        return result;
    }

    /**
     * 检查类是否有指定名称的方法
     */
    private boolean hasMethod(Class<?> clazz, String methodNamePrefix) {
        Method[] methods = clazz.getMethods();
        for (Method method : methods) {
            if (method.getName().equals(methodNamePrefix)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 安全获取Bean，不存在时返回null而不是抛出异常
     */
    private Object getBean(String beanName) {
        try {
            // 加载类
            Class<?> clazz = Class.forName(beanName, false, Thread.currentThread().getContextClassLoader());
            return applicationContext.getBean(clazz);
        } catch (BeansException | ClassNotFoundException e) {
            log.debug("Bean {} 不存在", beanName);
            return null;
        }
    }

    /**
     * 查找匹配的方法
     */
    private Method findMethod(Object implInstance, Class<?> clazz, String methodName, List<Object> params, Map<String, Object> result, String implName) {
        while (clazz != Objects.class && clazz != null) {
            Method[] methods = clazz.getDeclaredMethods();
            for (Method method : methods) {
                if (method.getName().equals(methodName)) {
                    Class<?>[] paramTypes = method.getParameterTypes();
                    if (params.isEmpty() && paramTypes.length == 0) {
                        method.setAccessible(true);
                        Object methodResult = null;
                        try {
                            methodResult = method.invoke(implInstance, (Object[]) null);
                        } catch (IllegalAccessException |
                                 InvocationTargetException ignored) {

                        }
                        result.put(implName + "#" + methodName, methodResult);
                        return method;
                    } else if (params.size() == paramTypes.length) {
                        boolean match = true;
                        Object[] objects = new Object[params.size()];
                        for (int i = 0; i < params.size(); i++) {
                            try {
                                if (params.get(i) != null) {
                                    // 使用增强的类型转换方法
                                    objects[i] = convertParameter(params.get(i), method, i, paramTypes[i]);
                                } else {
                                    objects[i] = null;
                                }
                            } catch (Exception e) {
                                log.warn("参数类型转换失败: 参数索引={}, 原始类型={}, 目标类型={}, 错误信息={}",
                                        i,
                                        params.get(i) != null ? params.get(i).getClass().getName() : "null",
                                        paramTypes[i].getName(),
                                        e.getMessage());
                                match = false;
                                break;
                            }
                        }
                        try {

                            Method method1 = getMethod(implInstance, methodName, result, implName, method, objects, match);
                            if (method1 != null) return method1;
                        } catch (Exception e) {
                            try {
                                try {
                                    Object targetObject = getTargetObject(implInstance);
                                    if (targetObject != null && targetObject != implInstance) {
                                        implInstance = targetObject;
                                        method = implInstance.getClass().getDeclaredMethod(methodName, paramTypes);
                                    }
                                }  catch (Exception ignored) {
                                }
                                Method method1 = getMethod(implInstance, methodName, result, implName, method, objects, match);
                                if (method1 != null) return method1;
                            } catch (Exception ex) {
                                log.warn("获取目标对象失败: {}", ex.getMessage());
                                }
                        }
                    }
                }
            }
            clazz = clazz.getSuperclass();
        }
        return null;
    }

    private static Method getMethod(Object implInstance, String methodName, Map<String, Object> result, String implName, Method method, Object[] objects, boolean match) throws IllegalAccessException, InvocationTargetException {
        method.setAccessible(true);
        Object methodResult = method.invoke(implInstance, objects);
        result.put(implName + "#" + methodName, methodResult);
        if (match) {
            return method;
        }
        return null;
    }

    public static Object getTargetObject(Object proxy) throws Exception {
        if (AopUtils.isAopProxy(proxy) && proxy instanceof Advised) {
            return ((Advised) proxy).getTargetSource().getTarget();
        }
        return proxy;
    }

    /**
     * 增强的参数类型转换方法
     * 支持更多复杂类型的自动推断和转换
     *
     * @param paramValue 原始参数值
     * @param method     目标方法
     * @param paramIndex 参数索引
     * @param targetType 目标类型
     * @return 转换后的参数值
     */
    private Object convertParameter(Object paramValue, Method method, int paramIndex, Class<?> targetType) {
        if (paramValue == null) {
            return null;
        }

        // 1. 获取方法参数的泛型信息（使用Spring的ResolvableType）
        ResolvableType resolvableType = null;
        if (method != null) {
            resolvableType = ResolvableType.forMethodParameter(method, paramIndex);
        } else {
            // 如果 method 为 null，尝试从 targetType 创建 ResolvableType
            resolvableType = ResolvableType.forClass(targetType);
        }

        // 2. 判断目标类型是否有泛型参数
        // 通过检查 ResolvableType 的泛型数量或底层 Type 是否为 ParameterizedType 来判断
        boolean hasGenerics = false;
        try {
            // 方法1: 检查是否有泛型参数（Spring 4.0+ 支持）
            ResolvableType[] generics = resolvableType.getGenerics();
            if (generics.length > 0) {
                hasGenerics = true;
            } else {
                // 方法2: 检查底层 Type 是否为 ParameterizedType
                Type type = resolvableType.getType();
                if (type instanceof ParameterizedType) {
                    ParameterizedType pt = (ParameterizedType) type;
                    Type[] actualTypeArguments = pt.getActualTypeArguments();
                    hasGenerics = actualTypeArguments != null && actualTypeArguments.length > 0;
                }
            }
        } catch (Exception e) {
            // 如果获取泛型信息失败，保守处理：假设有泛型，走转换逻辑
            log.debug("获取泛型信息失败，假设有泛型: {}", e.getMessage());
            hasGenerics = true;
        }

        // 3. 如果类型已经匹配且没有泛型，直接返回
        // 注意：对于有泛型的类型（如 List<Integer>），即使 isInstance 返回 true，
        // 由于类型擦除的原因，List<Integer> 和 List<Long> 在运行时都是 List 类型，
        // 但泛型不匹配，需要走转换逻辑来检查泛型匹配
        if (targetType.isInstance(paramValue) && !hasGenerics) {
            return paramValue;
        }

        log.debug("参数转换 - 索引: {}, 原始类型: {}, 目标类型: {}, 泛型信息: {}, 是否有泛型: {}",
                paramIndex, paramValue.getClass().getSimpleName(), targetType.getSimpleName(), resolvableType, hasGenerics);

        // 4. 处理基本类型和包装类型
        if (ClassUtils.isPrimitiveOrWrapper(targetType)) {
            return convertPrimitiveType(paramValue, targetType);
        }

        // 5. 处理String类型
        if (targetType == String.class) {
            return paramValue.toString();
        }

        // 6. 处理BigDecimal和BigInteger
        if (targetType == BigDecimal.class || targetType == BigInteger.class) {
            return convertNumericType(paramValue, targetType);
        }

        // 7. 处理日期时间类型
        if (isDateTimeType(targetType)) {
            return convertDateTimeType(paramValue, targetType);
        }

        // 8. 处理枚举类型
        if (targetType.isEnum()) {
            return convertEnumType(paramValue, targetType);
        }

        // 9. 处理数组类型
        if (targetType.isArray()) {
            return convertArrayType(paramValue, targetType, resolvableType);
        }

        // 10. 处理Collection类型（List, Set等）
        if (Collection.class.isAssignableFrom(targetType)) {
            return convertCollectionType(paramValue, targetType, resolvableType);
        }

        // 11. 处理Map类型
        if (Map.class.isAssignableFrom(targetType)) {
            return convertMapType(paramValue, targetType, resolvableType);
        }

        // 12. 处理自定义对象（POJO）
        return convertCustomObject(paramValue, targetType);
    }

    /**
     * 转换基本类型和包装类型
     */
    private Object convertPrimitiveType(Object value, Class<?> targetType) {
        // 使用Spring的ConversionService进行转换
        if (conversionService.canConvert(value.getClass(), targetType)) {
            return conversionService.convert(value, targetType);
        }

        // 降级处理：通过字符串转换
        String strValue = value.toString();
        if (targetType == Integer.class || targetType == int.class) {
            return Integer.valueOf(strValue);
        } else if (targetType == Long.class || targetType == long.class) {
            return Long.valueOf(strValue);
        } else if (targetType == Double.class || targetType == double.class) {
            return Double.valueOf(strValue);
        } else if (targetType == Float.class || targetType == float.class) {
            return Float.valueOf(strValue);
        } else if (targetType == Boolean.class || targetType == boolean.class) {
            return Boolean.valueOf(strValue);
        } else if (targetType == Short.class || targetType == short.class) {
            return Short.valueOf(strValue);
        } else if (targetType == Byte.class || targetType == byte.class) {
            return Byte.valueOf(strValue);
        }

        return value;
    }

    /**
     * 转换数值类型（BigDecimal, BigInteger）
     */
    private Object convertNumericType(Object value, Class<?> targetType) {
        String strValue = value.toString();
        if (targetType == BigDecimal.class) {
            return new BigDecimal(strValue);
        } else if (targetType == BigInteger.class) {
            return new BigInteger(strValue);
        }
        return value;
    }

    /**
     * 判断是否为日期时间类型
     */
    private boolean isDateTimeType(Class<?> type) {
        return type == Date.class ||
                type == LocalDate.class ||
                type == LocalDateTime.class ||
                type == java.sql.Date.class ||
                type == java.sql.Timestamp.class;
    }

    /**
     * 转换日期时间类型
     */
    private Object convertDateTimeType(Object value, Class<?> targetType) {
        // 使用Spring的ConversionService
        if (conversionService.canConvert(value.getClass(), targetType)) {
            return conversionService.convert(value, targetType);
        }

        // 降级处理：使用JSON序列化反序列化
        return JSON.parseObject(JSON.toJSONString(value), targetType);
    }

    /**
     * 转换枚举类型
     */
    @SuppressWarnings({"unchecked", "rawtypes"})
    private Object convertEnumType(Object value, Class<?> targetType) {
        if (value instanceof String) {
            // 字符串转枚举
            return Enum.valueOf((Class<Enum>) targetType, (String) value);
        } else if (value instanceof Number) {
            // 数字转枚举（通过ordinal）
            int ordinal = ((Number) value).intValue();
            Object[] enumConstants = targetType.getEnumConstants();
            if (ordinal >= 0 && ordinal < enumConstants.length) {
                return enumConstants[ordinal];
            }
        }
        return value;
    }

    /**
     * 转换数组类型
     */
    private Object convertArrayType(Object value, Class<?> targetType, ResolvableType resolvableType) {
        if (!(value instanceof Collection)) {
            // 如果不是集合，尝试转换为单元素数组
            Object array = Array.newInstance(targetType.getComponentType(), 1);
            Array.set(array, 0, convertParameter(value, null, 0, targetType.getComponentType()));
            return array;
        }

        Collection<?> collection = (Collection<?>) value;
        Class<?> componentType = targetType.getComponentType();
        Object array = Array.newInstance(componentType, collection.size());

        int index = 0;
        for (Object item : collection) {
            Object converted = convertCustomObject(item, componentType);
            Array.set(array, index++, converted);
        }

        return array;
    }

    /**
     * 转换Collection类型（List, Set等）
     */
    @SuppressWarnings({"unchecked", "rawtypes"})
    private Object convertCollectionType(Object value, Class<?> targetType, ResolvableType resolvableType) {
        if (!(value instanceof Collection)) {
            // 如果不是集合，尝试包装为单元素集合
            Collection result = createCollectionInstance(targetType);
            result.add(value);
            return result;
        }

        Collection<?> sourceCollection = (Collection<?>) value;

        // 空集合直接返回
        if (sourceCollection.isEmpty()) {
            return createCollectionInstance(targetType);
        }

        // 获取泛型元素类型
        ResolvableType elementType = resolvableType.getGeneric(0);
        Class<?> elementClass = elementType.resolve(Object.class);

        log.debug("Collection元素类型: {}", elementClass.getSimpleName());

        // 创建目标集合
        Collection result = createCollectionInstance(targetType);

        // 转换每个元素
        String jsonStr = JSON.toJSONString(sourceCollection);
        if (elementClass == Object.class || elementClass == Map.class) {
            // 如果元素类型未知或为Map，保持原样
            return JSON.parseObject(jsonStr, resolvableType.getType());
        } else {
            // 使用FastJSON转换为目标类型
            List<?> list = JSON.parseArray(jsonStr, elementClass);
            result.addAll(list);
            return result;
        }
    }

    /**
     * 创建Collection实例
     */
    @SuppressWarnings("rawtypes")
    private Collection createCollectionInstance(Class<?> collectionType) {
        if (collectionType == List.class || collectionType == Collection.class) {
            return new ArrayList();
        } else if (collectionType == Set.class) {
            return new HashSet();
        } else if (collectionType.isInterface()) {
            return new ArrayList();
        } else {
            try {
                return (Collection) collectionType.newInstance();
            } catch (Exception e) {
                return new ArrayList();
            }
        }
    }

    /**
     * 转换Map类型
     */
    private Object convertMapType(Object value, Class<?> targetType, ResolvableType resolvableType) {
        if (!(value instanceof Map)) {
            // 如果不是Map，尝试通过JSON转换
            String jsonStr = JSON.toJSONString(value);
            return JSON.parseObject(jsonStr, resolvableType.getType());
        }

        // 获取Key和Value的泛型类型
        ResolvableType keyType = resolvableType.getGeneric(0);
        ResolvableType valueType = resolvableType.getGeneric(1);

        Class<?> keyClass = keyType.resolve(Object.class);
        Class<?> valueClass = valueType.resolve(Object.class);

        log.debug("Map类型 - Key: {}, Value: {}", keyClass.getSimpleName(), valueClass.getSimpleName());

        // 如果泛型类型明确，使用FastJSON的ParameterizedType转换
        if (keyClass != Object.class || valueClass != Object.class) {
            Type mapType = new com.alibaba.fastjson.util.ParameterizedTypeImpl(
                    new Type[]{keyClass, valueClass},
                    null,
                    Map.class);
            String jsonStr = JSON.toJSONString(value);
            return JSON.parseObject(jsonStr, mapType);
        }

        // 否则保持原样，使用DisableSpecialKeyDetect保留数字类型
        String jsonStr = JSON.toJSONString(value);
        return JSON.parseObject(jsonStr, Map.class,
                com.alibaba.fastjson.parser.Feature.DisableSpecialKeyDetect);
    }

    /**
     * 转换自定义对象（POJO）
     */
    private Object convertCustomObject(Object value, Class<?> targetType) {
        // 使用Gson进行转换（保证兼容性）
        try {
            String jsonStr = gson.toJson(value);
            return gson.fromJson(jsonStr, targetType);
        } catch (Exception e) {
            log.warn("Gson转换失败，尝试使用FastJSON: {}", e.getMessage());
            // 降级使用FastJSON
            String jsonStr = JSON.toJSONString(value);
            return JSON.parseObject(jsonStr, targetType);
        }
    }

    /**
     * 服务对比请求
     */
    @Data
    public static class ServiceCompareRequest {
        /**
         * 服务名称，例如 ClazzLessonAcl#getClazzLessonByClazzes
         */
        private String serviceNameAndMethodName;

        /**
         * 参数
         */
        private List<Object> params;
    }
}