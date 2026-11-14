import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import java.nio.charset.StandardCharsets;

public class RedisSerializerProbe {
    public static void main(String[] args) {
        GenericJackson2JsonRedisSerializer s = new GenericJackson2JsonRedisSerializer();
        String mapJson = "{\"123\":{\"clazzNumber\":456,\"recommendType\":1}}";

        // 1) 老链路写法：redisTemplate.set(key, json) —— value 经 GenericJackson 序列化
        byte[] oldWritten = s.serialize(mapJson);
        System.out.println("[old-write] bytes = " + new String(oldWritten, StandardCharsets.UTF_8));

        // 2) 老链路读法：同一 serializer 反序列化老写法产物
        Object oldRead = s.deserialize(oldWritten);
        System.out.println("[old-read ] class = " + oldRead.getClass().getName());
        String casted = (String) oldRead;
        System.out.println("[old-read ] cast-to-String OK, startsWith{ = " + casted.startsWith("{"));

        // 3) V2 写法：StringRedisTemplate.set(key, json) —— Redis 里是原始 JSON 文本
        byte[] v2Written = mapJson.getBytes(StandardCharsets.UTF_8);
        System.out.println("[v2-write ] bytes = " + new String(v2Written, StandardCharsets.UTF_8));

        // 4) 老读法读 V2 写的值（corePreheatCache: userRenewalRedis.opsForValue().get）
        Object v2Read;
        try {
            v2Read = s.deserialize(v2Written);
            System.out.println("[v2-read  ] class = " + v2Read.getClass().getName());
        } catch (Exception e) {
            System.out.println("[v2-read  ] deserialize threw: " + e);
            return;
        }
        try {
            String v2Casted = (String) v2Read;
            System.out.println("[v2-read  ] cast-to-String OK: " + v2Casted.substring(0, Math.min(40, v2Casted.length())));
        } catch (ClassCastException e) {
            System.out.println("[v2-read  ] ClassCastException: " + e.getMessage());
        }
    }
}
