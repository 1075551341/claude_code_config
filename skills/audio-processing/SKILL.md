---
name: audio-processing
description: 当需要处理音频文件、音频编辑、格式转换、音频剪辑、降噪处理时调用此技能。触发词：音频处理、音频编辑、FFmpeg音频、音频转换、音频剪辑、音频降噪、音频编码、音乐处理。
---

# 音频处理

## 核心能力

**音频编辑、格式转换、降噪处理、音频分析。**

---

## 适用场景

- 音频格式转换
- 音频剪辑编辑
- 降噪处理
- 音频提取

---

## FFmpeg 音频命令

### 格式转换

```bash
# 基础转换
ffmpeg -i input.wav output.mp3

# 指定参数
ffmpeg -i input.wav -codec:a libmp3lame -qscale:a 2 output.mp3

# 批量转换
for f in *.wav; do
  ffmpeg -i "$f" -q:a 2 "${f%.wav}.mp3"
done
```

### 音频剪辑

```bash
# 截取片段
ffmpeg -i input.mp3 -ss 00:01:00 -to 00:02:00 -c copy output.mp3

# 合并音频
ffmpeg -f concat -i filelist.txt -c copy output.mp3

# 调整音量
ffmpeg -i input.mp3 -af "volume=2" output.mp3  # 2倍音量
ffmpeg -i input.mp3 -af "volume=0.5" output.mp3  # 半音量

# 提取音频
ffmpeg -i video.mp4 -vn -acodec copy audio.aac
```

---

## Python 音频处理

### Pydub

```python
from pydub import AudioSegment

# 加载音频
audio = AudioSegment.from_file("input.mp3")

# 剪辑
clip = audio[10000:20000]  # 10-20秒

# 调整音量
louder = audio + 10  # 增加10dB
quieter = audio - 10  # 减少10dB

# 合并
combined = audio1 + audio2

# 导出
audio.export("output.mp3", format="mp3", bitrate="192k")
```

### 降噪处理

```python
import noisereduce as nr
import librosa

# 加载音频
y, sr = librosa.load("input.wav")

# 降噪
reduced_noise = nr.reduce_noise(y=y, sr=sr)

# 保存
import soundfile as sf
sf.write("output.wav", reduced_noise, sr)
```

### 音频分析

```python
import librosa
import numpy as np

# 加载音频
y, sr = librosa.load("audio.wav")

# 时长
duration = librosa.get_duration(y=y, sr=sr)

# 节拍检测
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

# 频谱分析
D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)

# MFCC特征
mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
```

---

## 音频格式对比

| 格式 | 特点 | 适用场景 |
|------|------|----------|
| MP3 | 有损压缩、兼容性好 | 通用场景 |
| AAC | 压缩效率高 | 流媒体 |
| WAV | 无损、体积大 | 专业编辑 |
| FLAC | 无损压缩 | 音乐存储 |
| OGG | 开源免费 | Web音频 |

---

## 常用操作

### 音量标准化

```bash
# 归一化音量
ffmpeg -i input.mp3 -af "loudnorm" output.mp3

# 指定目标音量
ffmpeg -i input.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" output.mp3
```

### 淡入淡出

```bash
# 淡入
ffmpeg -i input.mp3 -af "afade=t=in:st=0:d=5" output.mp3

# 淡出
ffmpeg -i input.mp3 -af "afade=t=out:st=55:d=5" output.mp3
```

### 采样率转换

```bash
ffmpeg -i input.wav -ar 44100 output.wav
```

---

## 批量处理

```python
from pydub import AudioSegment
import os

def batch_convert(input_dir, output_dir, format='mp3'):
    for f in os.listdir(input_dir):
        if f.endswith(('.wav', '.flac', '.m4a')):
            audio = AudioSegment.from_file(os.path.join(input_dir, f))
            output_name = os.path.splitext(f)[0] + f'.{format}'
            audio.export(
                os.path.join(output_dir, output_name),
                format=format,
                bitrate='192k'
            )
```

---

## 注意事项

```
必须：
- 保留原始文件
- 检查采样率
- 验证输出质量
- 注意版权问题

避免：
- 多次有损压缩
- 忽略采样率差异
- 音量过大失真
- 不保存处理参数
```

---

## 相关技能

- `video-processing` - 视频处理
- `python-automation` - Python 自动化