


# CentOS7安装ffmpeg扩展
由于CentOS自带的[yum](https://so.csdn.net/so/search?q=yum&spm=1001.2101.3001.7020)库不包含ffmpeg软件包，因此借助第三方YUM源下载ffmpeg

1. rpm --import http://li.nux.ro/download/nux/RPM-GPG-KEY-nux.ro
2. rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
3. yum install ffmpeg ffmpeg-devel -y
4. ffmpeg -version
5. 备注 
	1. 1. /usr/bin/ffmpeg #安装的ffmpeg服务绝对地址
	2. /usr/bin/ffprobe   #安装的ffprobe服务绝对地

https://blog.csdn.net/zz_lkw/article/details/119326010


### 删除alias
unalias ffmpeg


1. **iftop**：用于实时监视网络流量，显示当前的网络连接以及其带宽利用率。

#### 可执行包


linux环境可执行文件: http://genshuixue-public.oss-cn-beijing.aliyuncs.com/origin_test/2024-02-28/16ba808b8016e6dea99071a9892ab41b/audio_transfer_av


windows可执行文件:  http://genshuixue-public.oss-cn-beijing.aliyuncs.com/origin_test/2024-02-28/2e051f81c4d6482001280cf2f34954d5/audio_transfer_av.exe



http://genshuixue-public.oss-cn-beijing.aliyuncs.com/origin_test/2024-02-28/3bf8d026f28d693d58d5cd9411766d62/audio_transfer_av.zip


https://github.com/foyoux/pilk


python 容器环境:  
https://container.baijia.com/portal/namespace/prod/app/0/pods/gh-tb-client-protection-web-598b4f475d-tvtmg/pod/gh-tb-client-protection-web-598b4f475d-tvtmg/container/gh-tb-client-protection-web/terminal/al-bj-uqun-k8s-production/prod

1.  yum groupinstall "Development Tools"





```python
import os.path
import os, pilk
import json
import av
import logging
# 禁用所有日志输出
logging.disable(logging.CRITICAL)
def calculate_random_file(file_path):
    return file_path

def to_pcm(in_path: str):
    """任意媒体文件转 pcm"""
    out_path = os.path.splitext(in_path)[0] + '.pcm'
    with av.open(in_path) as in_container:
        in_stream = in_container.streams.audio[0]
        sample_rate = in_stream.codec_context.sample_rate
        with av.open(out_path, 'w', 's16le') as out_container:
            out_stream = out_container.add_stream(
                'pcm_s16le',
                rate=sample_rate,
                layout='mono'
            )
            try:
               for frame in in_container.decode(in_stream):
                  frame.pts = None
                  for packet in out_stream.encode(frame):
                     out_container.mux(packet)
            except:
               pass
    return out_path, sample_rate

def transferToJavaJson(gson):
    return json.dumps(gson, ensure_ascii=False).replace("False","false").replace("True","true")

def convert_to_silk(media_path: str) -> str:
    """任意媒体文件转 silk, 返回silk路径"""
    try:
        container =  av.open(media_path)
        if container.duration / av.time_base > 60:
            return transferToJavaJson({
                "mp3_path": media_path,
                "success": False,
                "reason": f"时长超过60s, 当前mp3的时长为: {int(container.duration / av.time_base)} s"
            })
        pcm_path, sample_rate = to_pcm(media_path)
        silk_path = calculate_random_file(os.path.splitext(pcm_path)[0])  + '.silk'
        pilk.encode(pcm_path, silk_path, pcm_rate=sample_rate, tencent=True)
        return transferToJavaJson({
            "mp3_path": media_path,
            "silk_path": silk_path,
            "success": True,
            "time": int(pilk.get_duration(silk_path) / 1000)
        })
    except Exception as e:
        return transferToJavaJson({
            "mp3_path": media_path,
            "success": False,
            "reason": str(e)
        })
    finally:
        try:
            os.remove(pcm_path)
        except Exception:
            pass

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(transferToJavaJson({
            "mp3_path": "",
            "success": False,
            "reason": f"参数不够"
        }))
        exit(0)
    param = sys.argv[1].strip().strip("\n").strip("\r\n")
    if not os.path.exists(param):
        print(transferToJavaJson({
            "mp3_path": param,
            "success": False,
            "reason": f"文件不存在"
        }))
        exit(0)
    if  param[-4:] != ".mp3":
        print(transferToJavaJson({
            "mp3_path": param,
            "success": False,
            "reason": f"不是mp3文件"
        }))
        exit(0)
    print(convert_to_silk(param))


```


```python
import os.path
import os, pilk
from pydub import AudioSegment
import glob
import json
import subprocess
def convert_m4s_to_mp4(input_m4s, output_mp4):
    try:
        # 使用 
        
        ffmpeg 将 M4S 文件转换为 MP4 文件
        subprocess.run(['ffmpeg', '-i', input_m4s, output_mp4])
        print("转换成功！")
    except Exception as e:
        print(f"转换失败: {e}")


def convert_to_silk(media_path: str) -> str:
    """将输入的媒体文件转出为 silk, 并返回silk路径"""
    media = AudioSegment.from_file(media_path)
    pcm_path = os.path.basename(media_path)
    pcm_path = os.path.splitext(pcm_path)[0]
    silk_path = pcm_path + '.silk'
    pcm_path += '.pcm'
    media.export(pcm_path, 's16le', parameters=['-ar', str(media.frame_rate), '-ac', '1']).close()
    pilk.encode(pcm_path, silk_path, pcm_rate=media.frame_rate, tencent=True)
    print(json.dumps({
        "path": silk_path,
        "time": pilk.get_duration(silk_path)/1000
    }))
    return silk_path




def convert_to_mp3(silk_path: str) -> str:
    """将输入的silk文件转出为 mp3, 并返回mp3路径"""
    pcm_path = silk_path.replace(".silk", ".pcm")
    pilk.decode(silk_path, pcm_path)
    pcm_audio = AudioSegment.from_file(pcm_path, format="pcm", sample_width=2, channels=1, frame_rate=24000)
    mp3_path = pcm_path.replace(".pcm", ".mp3")
    pcm_audio.export(mp3_path, format="mp3",  parameters=["-b", "192k"])
    audio = AudioSegment.from_file(mp3_path, format="mp3")
    duration_in_seconds = len(audio) / 1000  # 将毫秒转换为秒
    print(json.dumps({
        "path": mp3_path,
        "time": duration_in_seconds
    }))


def _transferAudio(input_path, output_path):
    if not (input_path.find(".") != -1 and output_path.find(".") != -1):
        return
    try:
        input_format = input_path[input_path.find(".") + 1:]
        output_format = output_path[output_path.find(".") + 1:]
        audio = AudioSegment.from_file(input_path, format=input_format)
        # 将音频保存为MP3文件
        audio.export(output_path, format=output_format)
        print(f'{input_path} 转化成功, 转化后路径为: {output_path}')
    except Exception as e:
        convert_m4s_to_mp4(input_path, output_path)


def transferAudio(input_path, output_path):
    if input_path.rfind(".") != -1:
        if output_path.rfind(".") == -1:
            output_path = input_path[:input_path.rfind(".")+1] + output_path
        _transferAudio(input_path, output_path)
    elif input_path.rfind(".") == -1 and output_path.rfind(".") == -1:
        from concurrent.futures import ThreadPoolExecutor
        paths = glob.glob(f"*.{input_path}", recursive=False)
        t = ThreadPoolExecutor(min(4, len(paths)))
        paths = [os.path.join(os.getcwd(), path) for path in paths]
        results = [path.replace(input_path, output_path) for path in paths]
        for input,output in zip(paths, results):
            t.submit(_transferAudio,input, output)
if __name__ == '__main__':
    import sys
    path = ""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    elif len(sys.argv) == 1:
        path = input("请输入语音文件路径: ")
    if path.rfind(".mp3") != -1:
        convert_to_silk(path)
    elif path.rfind(".silk") != -1:
        convert_to_mp3(path)
    else:
        print("{}")
```




保存工作目录和索引状态 WIP on feature_mp3ToSilk: 11e2a1f25 Merge branch 'release' into feature_fix_chatroom_event_report


```java

    private static String doShell(String[] command){
        try {

            ProcessBuilder processBuilder = new ProcessBuilder(command);
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder res = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                res.append(line);
            }
            int exitCode = process.waitFor();
            return res.toString();
        } catch (IOException | InterruptedException e) {
            return "";
        }
    }

    @PostMapping("/testmp3ToSilk")
    public String testmp3ToSilk(@RequestBody ConsumerVo vo){
        String name = "silk/audio_transfer_av_mac";
        if (System.getProperty("os.name").toLowerCase().contains("linux")) {
            name =  "silk/audio_transfer_av";
        }
        String silkExePath = TestController.class.getClassLoader().getResource(name).getPath();
        String mp3Path = vo.mp3Path;
        doShell(new String[]{"chmod","a+x", silkExePath});
        return doShell(new String[] {silkExePath, mp3Path});
    }

    public static void main(String[] args) {
        String name = "silk/audio_transfer_av_mac";
        if (System.getProperty("os.name").toLowerCase().contains("linux")) {
            name =  "silk/audio_transfer_av";
        }
        String silkExePath = TestController.class.getClassLoader().getResource(name).getPath();
        String mp3Path = "/tmp/01qw21￥￥￥211sd/1111.mp3";

        doShell(new String[]{"chmod","a+x", silkExePath});
        log.info("{}",doShell(new String[] {silkExePath, mp3Path}));
    }

```


### **SILK** 编码格式 和 **Tencent** 系语音的关系：

> 此处 **Tencent** 系语音，仅以微信语音为例

1. 标准 **SILK** 文件以 `b'#!SILK_V3'` 开始，以 `b'\xFF\xFF'` 结束，中间为语音数据
2. 微信语音文件在标准 **SILK** 文件的开头插入了 `b'\x02'`，去除了结尾的 `b'\xFF\xFF'`，中间不变




在使用 **pilk** 之前，你还需清楚 **音频文件 `mp3, aac, m4a, flac, wav, ...`** 与 **语音文件** 之间的转换是借助 [**PCM raw data**](https://en.wikipedia.org/wiki/Pulse-code_modulation) 完成的


![[../壁纸/附件/screencapture-github-foyoux-pilk-2024-02-21-13_50_57.pdf]]