


### apifox 自动会获取浏览器下所有网页的Cookie 无需手动填写Cookie 非常赞




### 导入

项目设置-> 数据管理->导入数据
![[../壁纸/附件/Pasted image 20240728151601.png]]



##  前置操作
设置请求头

```javaScript
var traffic_env = pm.globals.get('traffic-env');

console.log(traffic_env)

pm.request.headers['traffic-env'] = traffic_env
```
![[../壁纸/附件/Pasted image 20240728150754.png]]

或者直接设置全局参数

![[../壁纸/附件/Pasted image 20240728150836.png]]


增加服务

![[../壁纸/附件/Pasted image 20250929151054.png]]


### json自定义比较内容 脚本

```
// ===== Apifox 后置脚本：JSON 差异对比（高优展示数组数量差异）=====

const response = pm.response.json();

// ===== 配置项 =====
const CONFIG = {
    // 数组排序字段优先级
    sortKeys: ["number", "id", "idx", "name", "code"],
    
    // 特定路径指定排序字段
    customSortKeys: {},
    
    // 值截断长度
    maxValueLength: 80
};

// 收集输出
let output = [];

// 关键差异（高优先级）
let criticalDiffs = [];

function log(text) {
    output.push(text);
}

function logCritical(text) {
    criticalDiffs.push(text);
}

// ===== 排序相关函数 =====

function getSortKey(arr, path) {
    const pathParts = path.split(".");
    const lastPart = pathParts[pathParts.length - 1].replace(/\[\d+\]/g, "");
    
    if (CONFIG.customSortKeys[lastPart]) {
        return CONFIG.customSortKeys[lastPart];
    }
    
    if (CONFIG.customSortKeys[path]) {
        return CONFIG.customSortKeys[path];
    }
    
    if (!arr || arr.length === 0 || typeof arr[0] !== "object") {
        return null;
    }
    
    const firstItem = arr[0];
    for (var i = 0; i < CONFIG.sortKeys.length; i++) {
        if (firstItem.hasOwnProperty(CONFIG.sortKeys[i])) {
            return CONFIG.sortKeys[i];
        }
    }
    
    return null;
}

function sortArray(arr, sortKey) {
    if (!sortKey || !arr || arr.length === 0) {
        return arr;
    }
    
    return arr.slice().sort(function(a, b) {
        const valA = a[sortKey];
        const valB = b[sortKey];
        
        if (valA === undefined && valB === undefined) return 0;
        if (valA === undefined) return 1;
        if (valB === undefined) return -1;
        
        if (typeof valA === "number" && typeof valB === "number") {
            return valA - valB;
        }
        
        return String(valA).localeCompare(String(valB));
    });
}

// ===== 核心函数 =====

function findKeys(dataItem) {
    const keys = Object.keys(dataItem);
    const v1Key = keys.find(function(k) { return k.includes("V1"); });
    const oldKey = keys.find(function(k) { return !k.includes("V1"); });
    return { v1Key: v1Key, oldKey: oldKey };
}

function isObject(val) {
    return val !== null && typeof val === "object" && !Array.isArray(val);
}

function formatValue(val) {
    if (typeof val === "object") {
        const str = JSON.stringify(val);
        return str.length > CONFIG.maxValueLength 
            ? str.substring(0, CONFIG.maxValueLength) + "..." 
            : str;
    }
    return String(val);
}

// 获取数组元素的标识信息
function getItemIdentifier(item, sortKey) {
    if (!item || typeof item !== "object") {
        return String(item);
    }
    
    // 优先使用排序字段
    if (sortKey && item[sortKey] !== undefined) {
        return sortKey + "=" + item[sortKey];
    }
    
    // 尝试常用标识字段
    var identifiers = ["number", "id", "name", "code", "idx"];
    for (var i = 0; i < identifiers.length; i++) {
        if (item[identifiers[i]] !== undefined) {
            return identifiers[i] + "=" + item[identifiers[i]];
        }
    }
    
    return JSON.stringify(item).substring(0, 50);
}

// 深度对比
function deepCompare(v1Obj, oldObj, path) {
    path = path || "";
    
    const result = {
        v1Only: [],
        oldOnly: [],
        different: [],
        same: [],
        arrayCountDiffs: []  // 新增：数组数量差异
    };
    
    const v1Keys = Object.keys(v1Obj || {});
    const oldKeys = Object.keys(oldObj || {});
    const allKeys = [];
    
    // 合并去重
    v1Keys.forEach(function(k) { if (allKeys.indexOf(k) === -1) allKeys.push(k); });
    oldKeys.forEach(function(k) { if (allKeys.indexOf(k) === -1) allKeys.push(k); });
    
    allKeys.forEach(function(key) {
        const currentPath = path ? path + "." + key : key;
        const v1Val = v1Obj ? v1Obj[key] : undefined;
        const oldVal = oldObj ? oldObj[key] : undefined;
        const v1Has = v1Obj ? v1Obj.hasOwnProperty(key) : false;
        const oldHas = oldObj ? oldObj.hasOwnProperty(key) : false;
        
        if (v1Has && !oldHas) {
            result.v1Only.push({ path: currentPath, value: v1Val });
            return;
        }
        
        if (!v1Has && oldHas) {
            result.oldOnly.push({ path: currentPath, value: oldVal });
            return;
        }
        
        if (v1Has && oldHas) {
            // 都是数组 - 检查数量差异
            if (Array.isArray(v1Val) && Array.isArray(oldVal)) {
                // 🔥 关键：检查数组数量差异
                if (v1Val.length !== oldVal.length) {
                    result.arrayCountDiffs.push({
                        path: currentPath,
                        v1Count: v1Val.length,
                        oldCount: oldVal.length,
                        diff: v1Val.length - oldVal.length
                    });
                }
                
                var arrayResult = compareArrays(v1Val, oldVal, currentPath);
                result.v1Only = result.v1Only.concat(arrayResult.v1Only);
                result.oldOnly = result.oldOnly.concat(arrayResult.oldOnly);
                result.different = result.different.concat(arrayResult.different);
                result.same = result.same.concat(arrayResult.same);
                result.arrayCountDiffs = result.arrayCountDiffs.concat(arrayResult.arrayCountDiffs);
            }
            // 都是对象
            else if (isObject(v1Val) && isObject(oldVal)) {
                var subResult = deepCompare(v1Val, oldVal, currentPath);
                result.v1Only = result.v1Only.concat(subResult.v1Only);
                result.oldOnly = result.oldOnly.concat(subResult.oldOnly);
                result.different = result.different.concat(subResult.different);
                result.same = result.same.concat(subResult.same);
                result.arrayCountDiffs = result.arrayCountDiffs.concat(subResult.arrayCountDiffs);
            }
            // 基本类型
            else if (v1Val === oldVal) {
                result.same.push({ path: currentPath, value: v1Val });
            } else {
                result.different.push({
                    path: currentPath,
                    v1Value: v1Val,
                    oldValue: oldVal
                });
            }
        }
    });
    
    return result;
}

// 数组对比（带排序和数量检查）
function compareArrays(v1Arr, oldArr, path) {
    const result = {
        v1Only: [],
        oldOnly: [],
        different: [],
        same: [],
        arrayCountDiffs: []
    };
    
    const sortKey = getSortKey(v1Arr.length > 0 ? v1Arr : oldArr, path);
    
    // 排序
    const sortedV1 = sortKey ? sortArray(v1Arr, sortKey) : v1Arr;
    const sortedOld = sortKey ? sortArray(oldArr, sortKey) : oldArr;
    
    // 如果是对象数组且有排序字段，按 key 匹配
    if (sortKey && sortedV1.length > 0 && typeof sortedV1[0] === "object") {
        return compareArraysByKey(sortedV1, sortedOld, path, sortKey);
    }
    
    // 按索引对比
    const maxLen = Math.max(sortedV1.length, sortedOld.length);
    
    for (var i = 0; i < maxLen; i++) {
        const currentPath = path + "[" + i + "]";
        const v1Item = sortedV1[i];
        const oldItem = sortedOld[i];
        
        if (i >= sortedV1.length) {
            result.oldOnly.push({ path: currentPath, value: oldItem });
        } else if (i >= sortedOld.length) {
            result.v1Only.push({ path: currentPath, value: v1Item });
        } else if (isObject(v1Item) && isObject(oldItem)) {
            var subResult = deepCompare(v1Item, oldItem, currentPath);
            result.v1Only = result.v1Only.concat(subResult.v1Only);
            result.oldOnly = result.oldOnly.concat(subResult.oldOnly);
            result.different = result.different.concat(subResult.different);
            result.same = result.same.concat(subResult.same);
            result.arrayCountDiffs = result.arrayCountDiffs.concat(subResult.arrayCountDiffs);
        } else if (v1Item === oldItem) {
            result.same.push({ path: currentPath, value: v1Item });
        } else {
            result.different.push({
                path: currentPath,
                v1Value: v1Item,
                oldValue: oldItem
            });
        }
    }
    
    return result;
}

// 按 key 匹配数组对比
function compareArraysByKey(v1Arr, oldArr, path, sortKey) {
    const result = {
        v1Only: [],
        oldOnly: [],
        different: [],
        same: [],
        arrayCountDiffs: []
    };
    
    // 建立旧版索引
    const oldMap = {};
    oldArr.forEach(function(item) {
        const keyVal = item[sortKey];
        if (keyVal !== undefined) {
            oldMap[String(keyVal)] = item;
        }
    });
    
    const matchedOldKeys = {};
    
    // 遍历 V1
    v1Arr.forEach(function(v1Item) {
        const keyVal = v1Item[sortKey];
        const keyStr = String(keyVal);
        const currentPath = path + "[" + sortKey + "=" + keyVal + "]";
        
        if (oldMap[keyStr]) {
            matchedOldKeys[keyStr] = true;
            var subResult = deepCompare(v1Item, oldMap[keyStr], currentPath);
            result.v1Only = result.v1Only.concat(subResult.v1Only);
            result.oldOnly = result.oldOnly.concat(subResult.oldOnly);
            result.different = result.different.concat(subResult.different);
            result.same = result.same.concat(subResult.same);
            result.arrayCountDiffs = result.arrayCountDiffs.concat(subResult.arrayCountDiffs);
        } else {
            result.v1Only.push({ 
                path: currentPath, 
                value: v1Item,
                isArrayItem: true
            });
        }
    });
    
    // 检查旧版未匹配项
    oldArr.forEach(function(oldItem) {
        const keyVal = oldItem[sortKey];
        const keyStr = String(keyVal);
        
        if (!matchedOldKeys[keyStr]) {
            const currentPath = path + "[" + sortKey + "=" + keyVal + "]";
            result.oldOnly.push({ 
                path: currentPath, 
                value: oldItem,
                isArrayItem: true
            });
        }
    });
    
    return result;
}

// ===== 输出函数 =====

function printResult(result, v1Count, oldCount) {
    
    // 🔥🔥🔥 最高优先级：顶层数组数量差异 🔥🔥🔥
    if (v1Count !== undefined && oldCount !== undefined && v1Count !== oldCount) {
        log("");
        log("🚨🚨🚨 【严重】顶层数组数量不一致 🚨🚨🚨");
        log("┌─────────────────────────────────────────");
        log("│  V1 返回数量:  " + v1Count + " 条");
        log("│  旧版返回数量: " + oldCount + " 条");
        log("│  差异: " + (v1Count > oldCount 
            ? "V1 多 " + (v1Count - oldCount) + " 条" 
            : "V1 少 " + (oldCount - v1Count) + " 条"));
        log("└─────────────────────────────────────────");
        
        logCritical("🚨 顶层数组: V1=" + v1Count + "条, 旧版=" + oldCount + "条, 差异=" + (v1Count - oldCount));
    }
    
    // 🔥🔥 高优先级：嵌套数组数量差异 🔥🔥
    if (result.arrayCountDiffs.length > 0) {
        log("");
        log("⚠️⚠️ 【重要】嵌套数组数量差异 (" + result.arrayCountDiffs.length + "处) ⚠️⚠️");
        log("┌─────────────────────────────────────────");
        result.arrayCountDiffs.forEach(function(item) {
            var diffText = item.diff > 0 
                ? "V1 多 " + item.diff + " 条"
                : "V1 少 " + Math.abs(item.diff) + " 条";
            log("│  " + item.path);
            log("│    V1: " + item.v1Count + "条 | 旧版: " + item.oldCount + "条 | " + diffText);
            
            logCritical("⚠️ " + item.path + ": V1=" + item.v1Count + ", 旧版=" + item.oldCount);
        });
        log("└─────────────────────────────────────────");
    }
    
    // 🔥 高优先级：V1 多出的数组元素
    var v1OnlyArrayItems = result.v1Only.filter(function(item) { return item.isArrayItem; });
    if (v1OnlyArrayItems.length > 0) {
        log("");
        log("🟢⬆️ 【注意】V1 多出的数组元素 (" + v1OnlyArrayItems.length + "个):");
        v1OnlyArrayItems.forEach(function(item) {
            log("   ➕ " + item.path);
            log("      " + formatValue(item.value));
        });
    }
    
    // 🔥 高优先级：V1 缺少的数组元素
    var oldOnlyArrayItems = result.oldOnly.filter(function(item) { return item.isArrayItem; });
    if (oldOnlyArrayItems.length > 0) {
        log("");
        log("🔴⬇️ 【注意】V1 缺少的数组元素 (" + oldOnlyArrayItems.length + "个):");
        oldOnlyArrayItems.forEach(function(item) {
            log("   ➖ " + item.path);
            log("      " + formatValue(item.value));
        });
    }
    
    // 普通优先级：V1 独有字段
    var v1OnlyFields = result.v1Only.filter(function(item) { return !item.isArrayItem; });
    if (v1OnlyFields.length > 0) {
        log("");
        log("🟢 V1 独有字段 (" + v1OnlyFields.length + "个):");
        v1OnlyFields.forEach(function(item) {
            log("   " + item.path + " = " + formatValue(item.value));
        });
    }
    
    // 普通优先级：旧版独有字段
    var oldOnlyFields = result.oldOnly.filter(function(item) { return !item.isArrayItem; });
    if (oldOnlyFields.length > 0) {
        log("");
        log("🔴 旧版独有字段 (" + oldOnlyFields.length + "个):");
        oldOnlyFields.forEach(function(item) {
            log("   " + item.path + " = " + formatValue(item.value));
        });
    }
    
    // 普通优先级：值不同
    if (result.different.length > 0) {
        log("");
        log("🔵 值不同的字段 (" + result.different.length + "个):");
        result.different.forEach(function(item) {
            log("   " + item.path);
            log("      V1:  " + formatValue(item.v1Value));
            log("      旧版: " + formatValue(item.oldValue));
        });
    }
    
    // 汇总
    log("");
    log("═══════════════════════════════════════════");
    log("📊 差异汇总:");
    log("───────────────────────────────────────────");
    if (v1Count !== undefined) {
        log("   📦 顶层数组: V1=" + v1Count + "条, 旧版=" + oldCount + "条");
    }
    log("   ⚠️  数组数量差异: " + result.arrayCountDiffs.length + " 处");
    log("   ➕ V1多出元素:   " + v1OnlyArrayItems.length + " 个");
    log("   ➖ V1缺少元素:   " + oldOnlyArrayItems.length + " 个");
    log("   🟢 V1独有字段:   " + v1OnlyFields.length + " 个");
    log("   🔴 旧版独有字段: " + oldOnlyFields.length + " 个");
    log("   🔵 值不同字段:   " + result.different.length + " 个");
    log("   ✅ 相同字段:     " + result.same.length + " 个");
    log("═══════════════════════════════════════════");
    
    // 最终判断
    var hasCriticalDiff = (v1Count !== oldCount) || 
                          result.arrayCountDiffs.length > 0 ||
                          v1OnlyArrayItems.length > 0 ||
                          oldOnlyArrayItems.length > 0;
    
    var hasAnyDiff = hasCriticalDiff || 
                     v1OnlyFields.length > 0 || 
                     oldOnlyFields.length > 0 || 
                     result.different.length > 0;
    
    if (!hasAnyDiff) {
        log("");
        log("🎉🎉🎉 两个版本完全一致！🎉🎉🎉");
    } else if (hasCriticalDiff) {
        log("");
        log("❌❌❌ 存在关键差异，请重点关注！❌❌❌");
    }
}

// ===== 主逻辑 =====

try {
    log("╔═══════════════════════════════════════════════════════════╗");
    log("║           JSON 差异对比工具 v2.0                          ║");
    log("║   🔥 高优展示数组数量差异                                  ║");
    log("╚═══════════════════════════════════════════════════════════╝");
    log("");
    log("⚙️ 排序字段优先级: " + CONFIG.sortKeys.join(" > "));
    
    response.data.forEach(function(dataItem, index) {
        log("");
        log("############################################################");
        log("📦 对比第 " + (index + 1) + " 组数据");
        log("############################################################");
        
        const keys = findKeys(dataItem);
        const v1Key = keys.v1Key;
        const oldKey = keys.oldKey;
        
        if (!v1Key || !oldKey) {
            log("⚠️ 未找到 V1 或旧版数据");
            return;
        }
        
        log("🔑 V1 Key:  " + v1Key);
        log("🔑 旧版 Key: " + oldKey);
        
        const v1Data = dataItem[v1Key];
        const oldData = dataItem[oldKey];
        
        var v1Count, oldCount;
        
        if (Array.isArray(v1Data) && Array.isArray(oldData)) {
            v1Count = v1Data.length;
            oldCount = oldData.length;
            
            log("");
            log("📊 顶层数组数量: V1=" + v1Count + "条, 旧版=" + oldCount + "条");
            
            const sortKey = getSortKey(v1Data.length > 0 ? v1Data : oldData, "root");
            
            if (sortKey) {
                log("💡 按字段 '" + sortKey + "' 排序匹配");
                
                var arrayResult = compareArraysByKey(
                    sortArray(v1Data, sortKey),
                    sortArray(oldData, sortKey),
                    "root",
                    sortKey
                );
                printResult(arrayResult, v1Count, oldCount);
            } else {
                var result = {
                    v1Only: [],
                    oldOnly: [],
                    different: [],
                    same: [],
                    arrayCountDiffs: []
                };
                
                const maxLen = Math.max(v1Data.length, oldData.length);
                
                for (var i = 0; i < maxLen; i++) {
                    if (i >= v1Data.length) {
                        result.oldOnly.push({
                            path: "root[" + i + "]",
                            value: oldData[i],
                            isArrayItem: true
                        });
                    } else if (i >= oldData.length) {
                        result.v1Only.push({
                            path: "root[" + i + "]",
                            value: v1Data[i],
                            isArrayItem: true
                        });
                    } else {
                        var subResult = deepCompare(v1Data[i], oldData[i], "root[" + i + "]");
                        result.v1Only = result.v1Only.concat(subResult.v1Only);
                        result.oldOnly = result.oldOnly.concat(subResult.oldOnly);
                        result.different = result.different.concat(subResult.different);
                        result.same = result.same.concat(subResult.same);
                        result.arrayCountDiffs = result.arrayCountDiffs.concat(subResult.arrayCountDiffs);
                    }
                }
                
                printResult(result, v1Count, oldCount);
            }
        } else {
            var result = deepCompare(v1Data, oldData, "");
            printResult(result);
        }
    });
    
    // 最后输出关键差异汇总
    if (criticalDiffs.length > 0) {
        log("");
        log("╔═══════════════════════════════════════════════════════════╗");
        log("║  🚨 关键差异汇总（复制用）                                 ║");
        log("╠═══════════════════════════════════════════════════════════╣");
        criticalDiffs.forEach(function(diff) {
            log("║  " + diff);
        });
        log("╚═══════════════════════════════════════════════════════════╝");
    }
    
} catch (error) {
    log("❌ 脚本执行出错: " + error.message);
    log("错误堆栈: " + error.stack);
}

// 最终输出
console.log(output.join("\n"));
```