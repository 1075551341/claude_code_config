---
name: youtube-tools
description: 下载YouTube视频
triggers: [下载YouTube视频, 获取YouTube字幕, 分析YouTube内容]
---

# YouTube 工具

## 核心能力

**视频下载、字幕提取、内容分析。**

---

## 适用场景

- YouTube视频下载
- 字幕/转录提取
- 视频内容分析
- 学习资源整理

---

## 工具安装

### yt-dlp安装

```bash
# Windows (使用pip)
pip install yt-dlp

# Windows (使用scoop)
scoop install yt-dlp

# macOS
brew install yt-dlp

# Linux
pip install yt-dlp
# 或
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp

# 更新
yt-dlp -U
```

### 依赖工具

```bash
# FFmpeg（用于合并视频音频）
# Windows (scoop)
scoop install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

---

## 视频下载

### 基础下载

```bash
# 下载最佳质量
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID"

# 指定格式
yt-dlp -f "best[ext=mp4]" "URL"

# 下载指定分辨率
yt-dlp -f "bestvideo[height<=1080]+bestaudio" "URL"

# 下载4K视频
yt-dlp -f "bestvideo[height=2160]+bestaudio" "URL"

# 仅下载音频
yt-dlp -x --audio-format mp3 "URL"
```

### 批量下载

```bash
# 下载播放列表
yt-dlp "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# 下载频道所有视频
yt-dlp "https://www.youtube.com/@ChannelName/videos"

# 下载多个视频（从文件）
yt-dlp -a urls.txt

# 限制下载数量
yt-dlp --playlist-end 10 "PLAYLIST_URL"

# 下载特定范围
yt-dlp --playlist-start 5 --playlist-end 10 "PLAYLIST_URL"
```

### 高级选项

```bash
# 指定输出文件名
yt-dlp -o "%(title)s.%(ext)s" "URL"

# 自定义输出路径
yt-dlp -o "~/Downloads/%(uploader)s/%(title)s.%(ext)s" "URL"

# 下载并嵌入缩略图
yt-dlp --embed-thumbnail "URL"

# 下载并嵌入字幕
yt-dlp --embed-subs --sub-langs "all" "URL"

# 限制下载速度
yt-dlp --limit-rate 1M "URL"

# 使用代理
yt-dlp --proxy "socks5://127.0.0.1:1080" "URL"
```

---

## 字幕提取

### 下载字幕

```bash
# 列出可用字幕
yt-dlp --list-subs "URL"

# 下载指定语言字幕
yt-dlp --write-subs --sub-langs "zh-Hans" "URL"

# 下载所有字幕
yt-dlp --write-subs --sub-langs "all" "URL"

# 下载自动生成字幕
yt-dlp --write-auto-subs --sub-langs "zh-Hans" "URL"

# 指定字幕格式
yt-dlp --write-subs --sub-langs "en" --sub-format srt "URL"
```

### 字幕格式转换

```python
import re

def vtt_to_srt(vtt_content):
    """
    将VTT字幕转换为SRT格式

    参数：
        vtt_content: VTT格式字幕内容

    返回：
        str: SRT格式字幕
    """
    # 移除VTT头部
    vtt_content = re.sub(r'WEBVTT.*\n', '', vtt_content)
    vtt_content = re.sub(r'Kind:.*\n', '', vtt_content)
    vtt_content = re.sub(r'Language:.*\n', '', vtt_content)

    # 转换时间格式
    # VTT: 00:00:00.000 --> 00:00:00.000
    # SRT: 00:00:00,000 --> 00:00:00,000
    srt_content = re.sub(r'(\d{2}:\d{2}:\d{2})\.(\d{3})', r'\1,\2', vtt_content)

    # 添加序号
    lines = srt_content.strip().split('\n\n')
    srt_lines = []
    for i, block in enumerate(lines, 1):
        srt_lines.append(f"{i}\n{block}")

    return '\n\n'.join(srt_lines)
```

### 字幕分析

```python
def analyze_subtitles(srt_file):
    """
    分析字幕文件

    参数：
        srt_file: SRT字幕文件路径

    返回：
        dict: 分析结果
    """
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取文本
    import re
    text_blocks = re.findall(r'\d+\n[\d:,]+ --> [\d:,]+\n(.+?)(?=\n\n|\Z)', content, re.DOTALL)

    full_text = ' '.join(text_blocks)
    full_text = re.sub(r'<[^>]+>', '', full_text)  # 移除标签

    # 统计
    words = full_text.split()
    total_words = len(words)
    unique_words = len(set(word.lower() for word in words))

    # 预估时长（假设平均每分钟150词）
    estimated_minutes = total_words / 150

    return {
        'total_words': total_words,
        'unique_words': unique_words,
        'estimated_duration_minutes': round(estimated_minutes, 1),
        'full_text': full_text
    }
```

---

## 视频信息获取

### 获取元数据

```bash
# 获取视频信息（JSON格式）
yt-dlp --dump-json "URL"

# 获取简略信息
yt-dlp --get-title "URL"
yt-dlp --get-description "URL"
yt-dlp --get-duration "URL"
yt-dlp --get-filename "URL"

# 打印视频信息
yt-dlp --print "%(title)s - %(duration)s - %(view_count)s views" "URL"
```

### Python获取信息

```python
import subprocess
import json

def get_video_info(url):
    """
    获取YouTube视频信息

    参数：
        url: 视频URL

    返回：
        dict: 视频信息
    """
    result = subprocess.run(
        ['yt-dlp', '--dump-json', url],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Error: {result.stderr}")

    info = json.loads(result.stdout)

    return {
        'title': info.get('title'),
        'description': info.get('description'),
        'duration': info.get('duration'),
        'view_count': info.get('view_count'),
        'like_count': info.get('like_count'),
        'uploader': info.get('uploader'),
        'upload_date': info.get('upload_date'),
        'categories': info.get('categories'),
        'tags': info.get('tags'),
    }
```

---

## 内容分析

### 视频摘要生成

```python
def summarize_video(url, api_key):
    """
    生成视频摘要

    参数：
        url: YouTube URL
        api_key: OpenAI API密钥

    返回：
        str: 视频摘要
    """
    import openai

    # 下载字幕
    import subprocess
    subprocess.run([
        'yt-dlp', '--write-subs', '--sub-langs', 'en',
        '--skip-download', '-o', 'temp', url
    ], capture_output=True)

    # 读取字幕
    with open('temp.en.vtt', 'r', encoding='utf-8') as f:
        subtitle = f.read()

    # 调用API生成摘要
    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "总结以下视频字幕内容，提取关键要点："},
            {"role": "user", "content": subtitle[:10000]}  # 限制长度
        ]
    )

    return response.choices[0].message.content
```

---

## 常用命令速查

```bash
# 基础下载
yt-dlp "URL"

# 最佳质量MP4
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" "URL"

# 1080p以下
yt-dlp -f "bestvideo[height<=1080]+bestaudio" "URL"

# 仅音频MP3
yt-dlp -x --audio-format mp3 "URL"

# 下载字幕
yt-dlp --write-subs --sub-langs "zh-Hans" --skip-download "URL"

# 下载缩略图
yt-dlp --write-thumbnail --skip-download "URL"

# 批量下载播放列表
yt-dlp -o "%(playlist_index)s-%(title)s.%(ext)s" "PLAYLIST_URL"

# 查看可用格式
yt-dlp -F "URL"
```

---

## 注意事项

```
合规使用：
- 遵守YouTube服务条款
- 尊重版权，仅下载有权限的内容
- 个人学习研究用途

技术注意：
- 部分视频需要登录（使用--cookies）
- 年龄限制视频需要验证
- 部分地区需要代理
```

---

## 相关技能

- `video-processing` - 视频处理
- `audio-processing` - 音频处理
- `content-research` - 内容研究