---
name: video-processing
description: 处理视频文件
triggers: [处理视频文件, 视频编辑, 格式转换, 视频压缩, 提取音频]
---

# 视频处理

## 核心能力

**视频编辑、格式转换、压缩优化、FFmpeg操作。**

---

## 适用场景

- 视频格式转换
- 视频剪辑编辑
- 视频压缩优化
- 音频提取

---

## FFmpeg 常用命令

### 格式转换

```bash
# 基础转换
ffmpeg -i input.mp4 output.avi

# 指定编码器
ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4

# 批量转换
for f in *.avi; do
  ffmpeg -i "$f" "${f%.avi}.mp4"
done
```

### 视频压缩

```bash
# 降低码率
ffmpeg -i input.mp4 -b:v 1M -b:a 128k output.mp4

# 降低分辨率
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

# CRF压缩（质量优先）
ffmpeg -i input.mp4 -crf 23 output.mp4

# 高效压缩
ffmpeg -i input.mp4 -c:v libx265 -crf 28 output.mp4
```

### 视频剪辑

```bash
# 截取片段
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:00 -c copy output.mp4

# 合并视频
ffmpeg -f concat -i filelist.txt -c copy output.mp4

# 去除音频
ffmpeg -i input.mp4 -an output.mp4

# 提取音频
ffmpeg -i input.mp4 -vn -acodec copy output.aac
```

---

## Python 视频处理

### MoviePy

```python
from moviepy.editor import VideoFileClip, concatenate_videoclips

# 加载视频
clip = VideoFileClip("input.mp4")

# 剪辑
subclip = clip.subclip(10, 20)  # 10-20秒

# 调整大小
resized = clip.resize(0.5)

# 添加文字
from moviepy.editor import TextClip
txt = TextClip("Hello", fontsize=70, color='white')
txt = txt.set_position('center').set_duration(5)

# 合并
final = concatenate_videoclips([clip1, clip2])

# 导出
final.write_videofile("output.mp4", fps=24)
```

### OpenCV

```python
import cv2

# 读取视频
cap = cv2.VideoCapture('input.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 处理帧
ret, frame = cap.read()
while ret:
    # 处理帧
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, frame = cap.read()

cap.release()
```

---

## 视频优化

### 质量与体积平衡

```bash
# CRF值参考
# 18-22: 高质量
# 23-28: 中等质量
# 29-35: 低质量

ffmpeg -i input.mp4 -crf 23 -preset medium output.mp4
```

### 编码器选择

| 编码器 | 特点 | 适用场景 |
|--------|------|----------|
| libx264 | 兼容性好 | 通用场景 |
| libx265 | 高效压缩 | 高清视频 |
| libvpx | WebM格式 | Web视频 |
| libaom-av1 | 最新标准 | 未来趋势 |

---

## 批量处理

```python
import os
import subprocess

def process_videos(input_dir, output_dir):
    for f in os.listdir(input_dir):
        if f.endswith('.mp4'):
            input_path = os.path.join(input_dir, f)
            output_path = os.path.join(output_dir, f)
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                output_path
            ]
            subprocess.run(cmd)
```

---

## 注意事项

```
必须：
- 保留原始文件
- 检查输出质量
- 测试兼容性
- 监控处理进度

避免：
- 过度压缩
- 丢失关键帧
- 音视频不同步
- 忽略版权问题
```

---

## 相关技能

- `audio-processing` - 音频处理
- `python-automation` - Python 自动化
- `performance-optimization` - 性能优化